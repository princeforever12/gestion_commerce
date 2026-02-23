import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product, delete_product, list_products
from pharmacy_pos.services.stock_service import add_stock


class ProductServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        ensure_default_admin()

    def test_create_product_requires_non_empty_name(self) -> None:
        with self.assertRaises(ValueError):
            create_product("   ", None, "Divers", 0, 1, 0, 0, False)

    def test_create_product_generates_barcode_when_missing(self) -> None:
        pid = create_product("Produit Auto", None, "Divers", 10, 12, 0, 2, False)
        self.assertGreater(pid, 0)

        products = [p for p in list_products() if p["id"] == pid]
        self.assertEqual(len(products), 1)
        self.assertTrue(products[0]["barcode"].startswith("AUTO"))

    def test_delete_product_without_history(self) -> None:
        pid = create_product("A supprimer", None, "Divers", 1, 2, 0, 0, False)
        delete_product(pid)

        product_ids = {p["id"] for p in list_products()}
        self.assertNotIn(pid, product_ids)

    def test_delete_product_with_stock_movement_is_blocked(self) -> None:
        pid = create_product("Avec mouvement", None, "Divers", 1, 2, 0, 0, False)
        add_stock(pid, "LOT-1", "2029-01-01", 2)

        with self.assertRaises(ValueError):
            delete_product(pid)


if __name__ == "__main__":
    unittest.main()
