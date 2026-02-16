from pharmacy_pos.database import db_cursor
from pharmacy_pos.services.stock_service import reserve_stock_fifo


def create_sale(cashier_id: int, items: list[dict], payment_method: str) -> int:
    """
    items: [{product_id:int, quantity:int, prescription_ok?:bool}]
    """
    if not items:
        raise ValueError("Le panier est vide")

    with db_cursor() as cur:
        total_ht = 0.0
        total_tva = 0.0

        prepared_lines: list[dict] = []
        for item in items:
            cur.execute(
                "SELECT id, sell_price, tva, requires_prescription FROM products WHERE id = ?",
                (item["product_id"],),
            )
            product = cur.fetchone()
            if product is None:
                raise ValueError(f"Produit introuvable: {item['product_id']}")

            if product["requires_prescription"] and not item.get("prescription_ok", False):
                raise ValueError(f"Ordonnance requise pour le produit #{product['id']}")

            qty = int(item["quantity"])
            allocations = reserve_stock_fifo(product["id"], qty)
            line_total = product["sell_price"] * qty
            line_tva = line_total * (product["tva"] / 100.0)
            total_ht += line_total
            total_tva += line_tva

            prepared_lines.append(
                {
                    "product_id": product["id"],
                    "unit_price": product["sell_price"],
                    "allocations": allocations,
                }
            )

        total_ttc = total_ht + total_tva

        cur.execute(
            """
            INSERT INTO sales(cashier_id, total_ht, total_tva, total_ttc, payment_method)
            VALUES(?, ?, ?, ?, ?)
            """,
            (cashier_id, total_ht, total_tva, total_ttc, payment_method),
        )
        sale_id = cur.lastrowid

        for line in prepared_lines:
            for batch_id, qty_taken in line["allocations"]:
                cur.execute(
                    """
                    INSERT INTO sale_items(sale_id, product_id, batch_id, quantity, unit_price, line_total)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sale_id,
                        line["product_id"],
                        batch_id,
                        qty_taken,
                        line["unit_price"],
                        line["unit_price"] * qty_taken,
                    ),
                )

                cur.execute(
                    """
                    INSERT INTO stock_movements(product_id, type, quantity, reason)
                    VALUES(?, 'OUT', ?, ?)
                    """,
                    (line["product_id"], qty_taken, f"Vente #{sale_id}"),
                )

        return sale_id


def list_sales(limit: int = 100) -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT s.id, u.username AS cashier, s.total_ttc, s.payment_method, s.created_at,
                   CASE WHEN sc.id IS NULL THEN 0 ELSE 1 END AS canceled
            FROM sales s
            JOIN users u ON u.id = s.cashier_id
            LEFT JOIN sale_cancellations sc ON sc.sale_id = s.id
            ORDER BY s.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def get_sale_items(sale_id: int) -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT p.name AS product_name, si.quantity, si.unit_price, si.line_total,
                   b.batch_number, si.id AS sale_item_id
            FROM sale_items si
            JOIN products p ON p.id = si.product_id
            JOIN batches b ON b.id = si.batch_id
            WHERE si.sale_id = ?
            ORDER BY si.id ASC
            """,
            (sale_id,),
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def get_sale_summary(sale_id: int) -> dict | None:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT s.id, u.username AS cashier, s.total_ht, s.total_tva, s.total_ttc,
                   s.payment_method, s.created_at,
                   CASE WHEN sc.id IS NULL THEN 0 ELSE 1 END AS canceled
            FROM sales s
            JOIN users u ON u.id = s.cashier_id
            LEFT JOIN sale_cancellations sc ON sc.sale_id = s.id
            WHERE s.id = ?
            """,
            (sale_id,),
        )
        row = cur.fetchone()
    return None if row is None else dict(row)


def cancel_sale(sale_id: int, reason: str = "Annulation ticket") -> None:
    with db_cursor() as cur:
        cur.execute("SELECT id FROM sales WHERE id = ?", (sale_id,))
        if cur.fetchone() is None:
            raise ValueError("Vente introuvable")

        cur.execute("SELECT id FROM sale_cancellations WHERE sale_id = ?", (sale_id,))
        if cur.fetchone() is not None:
            raise ValueError("Cette vente est déjà annulée")

        cur.execute(
            "SELECT product_id, batch_id, quantity FROM sale_items WHERE sale_id = ?",
            (sale_id,),
        )
        rows = cur.fetchall()
        if not rows:
            raise ValueError("Aucune ligne de vente à annuler")

        for row in rows:
            cur.execute(
                "UPDATE batches SET quantity = quantity + ? WHERE id = ?",
                (row["quantity"], row["batch_id"]),
            )
            cur.execute(
                "INSERT INTO stock_movements(product_id, type, quantity, reason) VALUES(?, 'IN', ?, ?)",
                (row["product_id"], row["quantity"], f"Annulation vente #{sale_id}"),
            )

        cur.execute(
            "INSERT INTO sale_cancellations(sale_id, reason) VALUES(?, ?)",
            (sale_id, reason),
        )


def return_sale_item(sale_item_id: int, quantity: int, reason: str = "Retour client") -> None:
    if quantity <= 0:
        raise ValueError("Quantité de retour invalide")

    with db_cursor() as cur:
        cur.execute(
            "SELECT id, sale_id, product_id, batch_id, quantity FROM sale_items WHERE id = ?",
            (sale_item_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError("Ligne de vente introuvable")

        cur.execute("SELECT id FROM sale_cancellations WHERE sale_id = ?", (row["sale_id"],))
        if cur.fetchone() is not None:
            raise ValueError("Retour impossible: ticket déjà annulé")

        cur.execute(
            "SELECT COALESCE(SUM(quantity), 0) AS returned_qty FROM returns WHERE sale_item_id = ?",
            (sale_item_id,),
        )
        returned_qty = cur.fetchone()["returned_qty"]
        available = row["quantity"] - returned_qty
        if quantity > available:
            raise ValueError("Quantité retour supérieure au disponible")

        cur.execute(
            "INSERT INTO returns(sale_item_id, quantity, reason) VALUES(?, ?, ?)",
            (sale_item_id, quantity, reason),
        )
        cur.execute(
            "UPDATE batches SET quantity = quantity + ? WHERE id = ?",
            (quantity, row["batch_id"]),
        )
        cur.execute(
            "INSERT INTO stock_movements(product_id, type, quantity, reason) VALUES(?, 'IN', ?, ?)",
            (row["product_id"], quantity, f"Retour ligne #{sale_item_id}"),
        )
