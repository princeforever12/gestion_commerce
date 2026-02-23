from datetime import date, timedelta

from pharmacy_pos.database import db_cursor
from pharmacy_pos.services.product_service import create_product
from pharmacy_pos.services.stock_service import add_stock


def _find_product_id_by_barcode(barcode: str) -> int | None:
    with db_cursor() as cur:
        cur.execute("SELECT id FROM products WHERE barcode = ?", (barcode,))
        row = cur.fetchone()
    return None if row is None else int(row["id"])


def seed_demo_products() -> int:
    """Injecte un jeu de données de démonstration.

    - N'ajoute que les produits démo manquants (idempotent par barcode).
    - Retourne le nombre de produits nouvellement créés.
    """
    soon = (date.today() + timedelta(days=45)).isoformat()
    mid = (date.today() + timedelta(days=180)).isoformat()
    far = (date.today() + timedelta(days=365)).isoformat()

    demo = [
        {
            "name": "Paracétamol 500mg",
            "barcode": "340001001",
            "category": "Antalgiques",
            "buy": 1200,
            "sell": 1800,
            "tva": 0,
            "min_stock": 20,
            "rx": False,
            "lots": [("P500-A", far, 80)],
        },
        {
            "name": "Amoxicilline 1g",
            "barcode": "340001002",
            "category": "Antibiotiques",
            "buy": 2500,
            "sell": 3500,
            "tva": 0,
            "min_stock": 10,
            "rx": True,
            "lots": [("AMOX-01", mid, 40)],
        },
        {
            "name": "Vitamine C 1000mg",
            "barcode": "340001003",
            "category": "Compléments",
            "buy": 900,
            "sell": 1500,
            "tva": 0,
            "min_stock": 15,
            "rx": False,
            "lots": [("VITC-02", soon, 25)],
        },
        {
            "name": "Gel Hydroalcoolique 250ml",
            "barcode": "340001004",
            "category": "Hygiène",
            "buy": 700,
            "sell": 1200,
            "tva": 0,
            "min_stock": 12,
            "rx": False,
            "lots": [("GEL-11", far, 35)],
        },
        {
            "name": "Masque Chirurgical (boîte)",
            "barcode": "340001005",
            "category": "Protection",
            "buy": 1500,
            "sell": 2300,
            "tva": 0,
            "min_stock": 8,
            "rx": False,
            "lots": [("MSK-04", mid, 18)],
        },
    ]

    created = 0
    for row in demo:
        product_id = _find_product_id_by_barcode(row["barcode"])
        if product_id is None:
            product_id = create_product(
                name=row["name"],
                barcode=row["barcode"],
                category_name=row["category"],
                buy_price=row["buy"],
                sell_price=row["sell"],
                tva=row["tva"],
                min_stock=row["min_stock"],
                requires_prescription=row["rx"],
            )
            created += 1
            for lot_num, expiry, qty in row["lots"]:
                add_stock(product_id, lot_num, expiry, qty, reason="Seed démo")

    return created
