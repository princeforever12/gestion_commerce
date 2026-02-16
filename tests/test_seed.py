import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.demo_seed_service import seed_demo_products
from pharmacy_pos.services.product_service import create_product, list_products


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

    def test_seed_runs_even_if_some_products_already_exist(self) -> None:
        create_product("Produit Libre", "FREE-001", "Divers", 10, 12, 0, 1, False)

        created = seed_demo_products()
        products = list_products()
        barcodes = {p["barcode"] for p in products}

        self.assertGreaterEqual(created, 5)
        self.assertIn("FREE-001", barcodes)
        self.assertIn("340001001", barcodes)
        self.assertIn("340001005", barcodes)


if __name__ == "__main__":
    unittest.main()
