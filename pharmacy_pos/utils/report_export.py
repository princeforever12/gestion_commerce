import csv
from pathlib import Path

from pharmacy_pos.services.report_service import daily_sales_summary, top_products
from pharmacy_pos.services.sales_service import list_sales
from pharmacy_pos.services.stock_service import get_expiring_batches, get_low_stock_products


def export_reports_csv(output_dir: str) -> list[str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    # 1) Resume du jour
    summary = daily_sales_summary()
    summary_file = out / "rapport_resume_jour.csv"
    with summary_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nb_ventes", "total_ht", "total_tva", "total_ttc"])
        writer.writeheader()
        writer.writerow(summary)
    created.append(str(summary_file))

    # 2) Top produits
    top = top_products(20)
    top_file = out / "rapport_top_produits.csv"
    with top_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "qty_vendue", "montant"])
        writer.writeheader()
        for row in top:
            writer.writerow(row)
    created.append(str(top_file))

    # 3) Historique ventes
    sales = list_sales(500)
    sales_file = out / "rapport_ventes.csv"
    with sales_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "cashier", "total_ttc", "payment_method", "created_at", "canceled"])
        writer.writeheader()
        for row in sales:
            writer.writerow(row)
    created.append(str(sales_file))

    # 4) Alertes stock bas
    low_stock = get_low_stock_products()
    low_file = out / "rapport_stock_bas.csv"
    with low_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "min_stock", "stock"])
        writer.writeheader()
        for row in low_stock:
            writer.writerow(row)
    created.append(str(low_file))

    # 5) Lots en péremption proche
    expiring = get_expiring_batches(90)
    exp_file = out / "rapport_peremption_90j.csv"
    with exp_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "product_name", "batch_number", "expiry_date", "quantity"])
        writer.writeheader()
        for row in expiring:
            writer.writerow(row)
    created.append(str(exp_file))

    return created
