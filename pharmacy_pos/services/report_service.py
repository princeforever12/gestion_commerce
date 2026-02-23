from pharmacy_pos.database import db_cursor

PERIOD_SQL = {
    "jour": "DATE(created_at) = DATE('now')",
    "semaine": "DATE(created_at) >= DATE('now', '-6 day')",
    "mois": "STRFTIME('%Y-%m', created_at) = STRFTIME('%Y-%m', 'now')",
    "annee": "STRFTIME('%Y', created_at) = STRFTIME('%Y', 'now')",
}


def _period_where(period: str) -> str:
    where = PERIOD_SQL.get(period)
    if where is None:
        raise ValueError("Période invalide. Valeurs: jour, semaine, mois, annee")
    return where


def sales_summary(period: str = "jour") -> dict:
    where = _period_where(period)
    with db_cursor() as cur:
        cur.execute(
            f"""
            SELECT
                COUNT(*) AS nb_ventes,
                COALESCE(SUM(total_ht), 0) AS total_ht,
                COALESCE(SUM(total_tva), 0) AS total_tva,
                COALESCE(SUM(total_ttc), 0) AS total_ttc
            FROM sales
            WHERE {where}
            """
        )
        row = cur.fetchone()
    return dict(row)


def daily_sales_summary() -> dict:
    return sales_summary("jour")


def top_products(limit: int = 5, period: str = "jour") -> list[dict]:
    where = _period_where(period)
    with db_cursor() as cur:
        cur.execute(
            f"""
            SELECT p.name, SUM(si.quantity) AS qty_vendue, SUM(si.line_total) AS montant
            FROM sale_items si
            JOIN products p ON p.id = si.product_id
            JOIN sales s ON s.id = si.sale_id
            WHERE {where}
            GROUP BY p.id
            ORDER BY qty_vendue DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]
