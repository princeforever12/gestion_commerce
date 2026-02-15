from pharmacy_pos.database import db_cursor


def daily_sales_summary() -> dict:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT
                COUNT(*) AS nb_ventes,
                COALESCE(SUM(total_ht), 0) AS total_ht,
                COALESCE(SUM(total_tva), 0) AS total_tva,
                COALESCE(SUM(total_ttc), 0) AS total_ttc
            FROM sales
            WHERE DATE(created_at) = DATE('now')
            """
        )
        row = cur.fetchone()
    return dict(row)


def top_products(limit: int = 5) -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT p.name, SUM(si.quantity) AS qty_vendue, SUM(si.line_total) AS montant
            FROM sale_items si
            JOIN products p ON p.id = si.product_id
            GROUP BY p.id
            ORDER BY qty_vendue DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]
