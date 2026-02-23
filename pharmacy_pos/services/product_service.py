import time
from random import randint

from pharmacy_pos.database import db_cursor


def create_category(name: str) -> int:
    with db_cursor() as cur:
        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (name,))
        cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
        return cur.fetchone()["id"]


def generate_barcode() -> str:
    stamp = int(time.time() * 1000)
    suffix = randint(100, 999)
    return f"AUTO{stamp}{suffix}"


def create_product(
    name: str,
    barcode: str | None,
    category_name: str,
    buy_price: float,
    sell_price: float,
    tva: float,
    min_stock: int,
    requires_prescription: bool,
) -> int:
    name = name.strip()
    category_name = category_name.strip()

    if not name:
        raise ValueError("Le nom du produit est obligatoire")
    if not category_name:
        raise ValueError("La catégorie du produit est obligatoire")
    if buy_price < 0 or sell_price < 0 or tva < 0 or min_stock < 0:
        raise ValueError("Les valeurs numériques doivent être positives")

    clean_barcode = (barcode or "").strip()
    if not clean_barcode:
        clean_barcode = generate_barcode()

    category_id = create_category(category_name)
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO products(
                name, barcode, category_id, buy_price, sell_price,
                tva, requires_prescription, min_stock
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                clean_barcode,
                category_id,
                buy_price,
                sell_price,
                tva,
                int(requires_prescription),
                min_stock,
            ),
        )
        return cur.lastrowid


def delete_product(product_id: int) -> None:
    with db_cursor() as cur:
        cur.execute("SELECT id FROM products WHERE id = ?", (product_id,))
        if cur.fetchone() is None:
            raise ValueError("Produit introuvable")

        cur.execute("SELECT COUNT(*) AS n FROM sale_items WHERE product_id = ?", (product_id,))
        if cur.fetchone()["n"] > 0:
            raise ValueError("Suppression impossible: produit déjà lié à des ventes")

        cur.execute("SELECT COUNT(*) AS n FROM stock_movements WHERE product_id = ?", (product_id,))
        if cur.fetchone()["n"] > 0:
            raise ValueError("Suppression impossible: produit déjà lié à des mouvements de stock")

        cur.execute("DELETE FROM products WHERE id = ?", (product_id,))


def list_products() -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT p.id, p.name, p.barcode, c.name AS category,
                   p.buy_price, p.sell_price, p.tva, p.min_stock,
                   p.requires_prescription,
                   COALESCE(SUM(b.quantity), 0) AS stock
            FROM products p
            LEFT JOIN categories c ON c.id = p.category_id
            LEFT JOIN batches b ON b.product_id = p.id
            GROUP BY p.id
            ORDER BY p.name ASC
            """
        )
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def search_products(term: str, limit: int = 30) -> list[dict]:
    clean = term.strip()
    with db_cursor() as cur:
        if not clean:
            cur.execute(
                """
                SELECT id, name, barcode, sell_price, requires_prescription
                FROM products
                ORDER BY name ASC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            like = f"%{clean}%"
            cur.execute(
                """
                SELECT id, name, barcode, sell_price, requires_prescription
                FROM products
                WHERE name LIKE ? OR barcode LIKE ?
                ORDER BY name ASC
                LIMIT ?
                """,
                (like, like, limit),
            )
        rows = cur.fetchall()
    return [dict(row) for row in rows]
