import unittest

from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.sales_service import create_sale, get_sale_items, list_sales
from pharmacy_pos.services.stock_service import add_stock, get_total_stock


class SalesFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        # reset database file by recreating tables quickly
        import os
        from pharmacy_pos.config import DB_PATH

        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        ensure_default_admin()

    def test_sale_decrements_stock_fifo(self) -> None:
        product_id = create_product("Paracetamol", "111", "Analgesique", 10, 15, 18, 5, False)
        add_stock(product_id, "L1", "2026-01-01", 3)
        add_stock(product_id, "L2", "2026-06-01", 5)

        sale_id = create_sale(1, [{"product_id": product_id, "quantity": 4}], "cash")

        self.assertGreater(sale_id, 0)
        self.assertEqual(get_total_stock(product_id), 4)

    def test_sale_history_and_items(self) -> None:
        product_id = create_product("Doliprane", "777", "Analgesique", 5, 9, 0, 1, False)
        add_stock(product_id, "D1", "2028-01-01", 10)
        sale_id = create_sale(1, [{"product_id": product_id, "quantity": 2}], "carte")

        sales = list_sales()
        self.assertGreaterEqual(len(sales), 1)
        self.assertEqual(sales[0]["id"], sale_id)

        items = get_sale_items(sale_id)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["product_name"], "Doliprane")
        self.assertEqual(items[0]["quantity"], 2)


if __name__ == "__main__":
    unittest.main()
