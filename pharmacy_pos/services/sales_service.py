from pharmacy_pos.database import db_cursor
from pharmacy_pos.services.stock_service import reserve_stock_fifo


def create_sale(cashier_id: int, items: list[dict], payment_method: str) -> int:
    """
    items: [{product_id:int, quantity:int}]
    """
    if not items:
        raise ValueError("Le panier est vide")

    with db_cursor() as cur:
        total_ht = 0.0
        total_tva = 0.0

        prepared_lines: list[dict] = []
        for item in items:
            cur.execute(
                "SELECT id, sell_price, tva FROM products WHERE id = ?",
                (item["product_id"],),
            )
            product = cur.fetchone()
            if product is None:
                raise ValueError(f"Produit introuvable: {item['product_id']}")

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
                    "quantity": qty,
                    "line_total": line_total,
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
            SELECT s.id, u.username AS cashier, s.total_ttc, s.payment_method, s.created_at
            FROM sales s
            JOIN users u ON u.id = s.cashier_id
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
            SELECT p.name AS product_name, si.quantity, si.unit_price, si.line_total, b.batch_number
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
