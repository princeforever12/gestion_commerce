import os
import tempfile
import unittest

from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.product_service import create_product, search_products
from pharmacy_pos.services.sales_service import (
    cancel_sale,
    create_sale,
    get_sale_items,
    get_sale_summary,
    list_sales,
    return_sale_item,
)
from pharmacy_pos.services.stock_service import add_stock, get_total_stock
from pharmacy_pos.utils.ticket_export import export_ticket_text, render_ticket_text


class SalesFlowTest(unittest.TestCase):
    def setUp(self) -> None:
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

    def test_sale_history_items_and_ticket_export(self) -> None:
        product_id = create_product("Doliprane", "777", "Analgesique", 5, 9, 0, 1, False)
        add_stock(product_id, "D1", "2028-01-01", 10)
        sale_id = create_sale(1, [{"product_id": product_id, "quantity": 2}], "carte")

        sales = list_sales()
        self.assertGreaterEqual(len(sales), 1)
        self.assertEqual(sales[0]["id"], sale_id)

        summary = get_sale_summary(sale_id)
        self.assertIsNotNone(summary)
        self.assertEqual(summary["payment_method"], "carte")

        items = get_sale_items(sale_id)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["product_name"], "Doliprane")
        self.assertEqual(items[0]["quantity"], 2)

        ticket = render_ticket_text(sale_id)
        self.assertIn("PHARMACIE POS - TICKET", ticket)
        self.assertIn("Doliprane", ticket)

        with tempfile.TemporaryDirectory() as tmp:
            out = export_ticket_text(sale_id, os.path.join(tmp, "ticket_test.txt"))
            self.assertTrue(os.path.exists(out))

    def test_prescription_required_product(self) -> None:
        product_id = create_product("Antibiotique", "999", "Rx", 4, 10, 0, 1, True)
        add_stock(product_id, "RX1", "2028-05-01", 5)

        with self.assertRaises(ValueError):
            create_sale(1, [{"product_id": product_id, "quantity": 1}], "cash")

        sale_id = create_sale(
            1,
            [{"product_id": product_id, "quantity": 1, "prescription_ok": True}],
            "cash",
        )
        self.assertGreater(sale_id, 0)

    def test_search_products_by_name_and_barcode(self) -> None:
        create_product("Amoxicilline", "ABC123", "Rx", 2, 6, 0, 1, True)
        create_product("Vitamine D", "VITD", "Supp", 1, 3, 0, 1, False)

        by_name = search_products("amoxi")
        self.assertEqual(len(by_name), 1)
        self.assertEqual(by_name[0]["name"], "Amoxicilline")

        by_barcode = search_products("VITD")
        self.assertEqual(len(by_barcode), 1)
        self.assertEqual(by_barcode[0]["name"], "Vitamine D")

    def test_cancel_sale_restores_stock(self) -> None:
        product_id = create_product("Masque", "MSK", "Divers", 1, 2, 0, 1, False)
        add_stock(product_id, "M1", "2029-01-01", 10)
        sale_id = create_sale(1, [{"product_id": product_id, "quantity": 4}], "cash")
        self.assertEqual(get_total_stock(product_id), 6)

        cancel_sale(sale_id, "Erreur ticket")
        self.assertEqual(get_total_stock(product_id), 10)

        summary = get_sale_summary(sale_id)
        self.assertEqual(summary["canceled"], 1)

    def test_return_sale_item_restores_partial_stock(self) -> None:
        product_id = create_product("Gel", "GEL1", "Divers", 1, 4, 0, 1, False)
        add_stock(product_id, "G1", "2029-01-01", 10)
        sale_id = create_sale(1, [{"product_id": product_id, "quantity": 5}], "cash")
        self.assertEqual(get_total_stock(product_id), 5)

        items = get_sale_items(sale_id)
        sale_item_id = items[0]["sale_item_id"]
        return_sale_item(sale_item_id, 2, "Produit non conforme")

        self.assertEqual(get_total_stock(product_id), 7)


if __name__ == "__main__":
    unittest.main()
