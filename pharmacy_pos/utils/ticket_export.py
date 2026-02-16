from pathlib import Path

from pharmacy_pos.services.sales_service import get_sale_items, get_sale_summary


def render_ticket_text(sale_id: int) -> str:
    sale = get_sale_summary(sale_id)
    if sale is None:
        raise ValueError("Vente introuvable")

    items = get_sale_items(sale_id)
    lines = [
        "PHARMACIE POS - TICKET",
        f"Ticket: #{sale['id']}",
        f"Date: {sale['created_at']}",
        f"Caissier: {sale['cashier']}",
        f"Paiement: {sale['payment_method']}",
        "-" * 36,
    ]

    for item in items:
        lines.append(
            f"{item['product_name']} x{item['quantity']} @ {item['unit_price']:.2f} = {item['line_total']:.2f}"
        )

    lines.extend(
        [
            "-" * 36,
            f"TOTAL HT: {sale['total_ht']:.2f}",
            f"TOTAL TVA: {sale['total_tva']:.2f}",
            f"TOTAL TTC: {sale['total_ttc']:.2f}",
        ]
    )
    return "\n".join(lines) + "\n"


def export_ticket_text(sale_id: int, path: str) -> str:
    content = render_ticket_text(sale_id)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return str(out)
