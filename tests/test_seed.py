import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.demo_seed_service import seed_demo_products
from pharmacy_pos.services.product_service import list_products


class SeedDemoTest(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        ensure_default_admin()

    def test_seed_demo_products_idempotent(self) -> None:
        first = seed_demo_products()
        second = seed_demo_products()

        products = list_products()

        self.assertGreaterEqual(first, 5)
        self.assertEqual(second, 0)
        self.assertGreaterEqual(len(products), 5)


if __name__ == "__main__":
    unittest.main()
