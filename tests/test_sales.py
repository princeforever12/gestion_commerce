import unittest

from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.sales_service import create_sale
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


if __name__ == "__main__":
    unittest.main()
