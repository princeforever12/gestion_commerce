import os
import tempfile
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import db_cursor, init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.report_service import daily_sales_summary, sales_summary
from pharmacy_pos.services.sales_service import create_sale
from pharmacy_pos.services.stock_service import add_stock
from pharmacy_pos.utils.report_export import export_reports_csv


class ReportTest(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        ensure_default_admin()

    def test_daily_summary_has_totals(self) -> None:
        product_id = create_product("Ibuprofene", "333", "Analgesique", 12, 20, 10, 2, False)
        add_stock(product_id, "IBU-1", "2027-02-02", 10)
        create_sale(1, [{"product_id": product_id, "quantity": 2}], "carte")

        summary = daily_sales_summary()

        self.assertEqual(summary["nb_ventes"], 1)
        self.assertAlmostEqual(summary["total_ht"], 40)
        self.assertAlmostEqual(summary["total_tva"], 4)
        self.assertAlmostEqual(summary["total_ttc"], 44)

    def test_sales_summary_periods(self) -> None:
        product_id = create_product("Sirop", "S111", "Divers", 3, 7, 0, 2, False)
        add_stock(product_id, "S-LOT", "2029-01-01", 20)
        current_sale = create_sale(1, [{"product_id": product_id, "quantity": 1}], "cash")
        old_sale = create_sale(1, [{"product_id": product_id, "quantity": 1}], "cash")

        with db_cursor() as cur:
            cur.execute(
                "UPDATE sales SET created_at = DATETIME('now', '-10 day') WHERE id = ?",
                (old_sale,),
            )
            cur.execute(
                "UPDATE sales SET created_at = DATETIME('now') WHERE id = ?",
                (current_sale,),
            )

        day = sales_summary("jour")
        week = sales_summary("semaine")
        month = sales_summary("mois")
        year = sales_summary("annee")

        self.assertEqual(day["nb_ventes"], 1)
        self.assertEqual(week["nb_ventes"], 1)
        self.assertGreaterEqual(month["nb_ventes"], 1)
        self.assertGreaterEqual(year["nb_ventes"], 1)

    def test_export_reports_csv(self) -> None:
        product_id = create_product("Sirop", "S112", "Divers", 3, 7, 0, 2, False)
        add_stock(product_id, "S-LOT", "2029-01-01", 20)
        create_sale(1, [{"product_id": product_id, "quantity": 3}], "cash")

        with tempfile.TemporaryDirectory() as tmp:
            files = export_reports_csv(tmp)

            self.assertGreaterEqual(len(files), 5)
            for path in files:
                self.assertTrue(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
