from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import ensure_default_admin


def bootstrap() -> None:
    """Initialise la base et les données minimales nécessaires au lancement."""
    init_db()
    ensure_default_admin()
