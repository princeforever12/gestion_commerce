from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin
from pharmacy_pos.services.demo_seed_service import seed_demo_products


def bootstrap() -> None:
    """Initialise la base et les données minimales nécessaires au lancement."""
    init_db()
    ensure_default_admin()
    seed_demo_products()
