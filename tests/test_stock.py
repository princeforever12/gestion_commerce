import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.stock_service import add_stock, get_low_stock_products


class StockAlertTest(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()

    def test_low_stock_alert(self) -> None:
        product_id = create_product("Vitamine C", "222", "Supplements", 5, 8, 0, 10, False)
        add_stock(product_id, "VIT-1", "2027-01-01", 6)

        alerts = get_low_stock_products()

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["id"], product_id)


if __name__ == "__main__":
    unittest.main()
