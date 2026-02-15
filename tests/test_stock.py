import os
import unittest
from datetime import date, timedelta

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.sales_service import create_sale
from pharmacy_pos.services.stock_service import add_stock, get_expiring_batches, get_low_stock_products


class StockAlertTest(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        ensure_default_admin()

    def test_low_stock_alert(self) -> None:
        product_id = create_product("Vitamine C", "222", "Supplements", 5, 8, 0, 10, False)
        add_stock(product_id, "VIT-1", "2027-01-01", 6)

        alerts = get_low_stock_products()

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["id"], product_id)

    def test_expired_batch_is_excluded_from_sale(self) -> None:
        product_id = create_product("Sirop", "444", "Divers", 2, 4, 0, 1, False)
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        add_stock(product_id, "LOT-OLD", yesterday, 5)
        add_stock(product_id, "LOT-NEW", tomorrow, 2)

        with self.assertRaises(ValueError):
            create_sale(1, [{"product_id": product_id, "quantity": 3}], "cash")

    def test_get_expiring_batches(self) -> None:
        product_id = create_product("Gel", "555", "Divers", 1, 2, 0, 1, False)
        soon = (date.today() + timedelta(days=10)).isoformat()
        far = (date.today() + timedelta(days=180)).isoformat()
        add_stock(product_id, "GEL-10", soon, 1)
        add_stock(product_id, "GEL-180", far, 1)

        rows = get_expiring_batches(90)
        batch_numbers = [r["batch_number"] for r in rows]

        self.assertIn("GEL-10", batch_numbers)
        self.assertNotIn("GEL-180", batch_numbers)


if __name__ == "__main__":
    unittest.main()
