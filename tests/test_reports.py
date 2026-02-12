import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.report_service import daily_sales_summary
from pharmacy_pos.services.sales_service import create_sale
from pharmacy_pos.services.stock_service import add_stock


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


if __name__ == "__main__":
    unittest.main()
