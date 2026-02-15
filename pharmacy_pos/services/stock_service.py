from pharmacy_pos.database import db_cursor


def add_stock(product_id: int, batch_number: str, expiry_date: str, quantity: int, reason: str = "Approvisionnement") -> int:
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO batches(product_id, batch_number, expiry_date, quantity) VALUES(?, ?, ?, ?)",
            (product_id, batch_number, expiry_date, quantity),
        )
        batch_id = cur.lastrowid
        cur.execute(
            "INSERT INTO stock_movements(product_id, type, quantity, reason) VALUES(?, 'IN', ?, ?)",
            (product_id, quantity, reason),
        )
        return batch_id


def get_total_stock(product_id: int) -> int:
    with db_cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(quantity), 0) AS total FROM batches WHERE product_id = ?", (product_id,))
        return cur.fetchone()["total"]


def get_low_stock_products() -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.name, p.min_stock, COALESCE(SUM(b.quantity), 0) AS stock
            FROM products p
            LEFT JOIN batches b ON b.product_id = p.id
            GROUP BY p.id
            HAVING stock <= p.min_stock
            ORDER BY stock ASC
            """
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def get_expiring_batches(days: int = 90) -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT b.id, p.name AS product_name, b.batch_number, b.expiry_date, b.quantity
            FROM batches b
            JOIN products p ON p.id = b.product_id
            WHERE b.quantity > 0
              AND DATE(b.expiry_date) <= DATE('now', '+' || ? || ' day')
            ORDER BY DATE(b.expiry_date) ASC
            """,
            (days,),
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def reserve_stock_fifo(product_id: int, quantity: int) -> list[tuple[int, int]]:
    """Retourne liste de (batch_id, qty_pris) en FIFO par date de péremption.
    Les lots expirés sont exclus.
    """
    remaining = quantity
    allocations: list[tuple[int, int]] = []

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, quantity
            FROM batches
            WHERE product_id = ?
              AND quantity > 0
              AND DATE(expiry_date) >= DATE('now')
            ORDER BY expiry_date ASC, id ASC
            """,
            (product_id,),
        )
        batches = cur.fetchall()

        for batch in batches:
            if remaining <= 0:
                break
            available = batch["quantity"]
            take = min(available, remaining)
            if take > 0:
                allocations.append((batch["id"], take))
                remaining -= take

        if remaining > 0:
            raise ValueError("Stock insuffisant (lots valides non expirés)")

        for batch_id, take in allocations:
            cur.execute("UPDATE batches SET quantity = quantity - ? WHERE id = ?", (take, batch_id))

    return allocations
