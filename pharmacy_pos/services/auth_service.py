import hashlib
from dataclasses import dataclass

from pharmacy_pos.database import db_cursor

VALID_ROLES = {"admin", "caissier", "pharmacien"}


@dataclass
class User:
    id: int
    username: str
    role: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_default_admin() -> None:
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users(username, password_hash, role) VALUES(?, ?, ?)",
                ("admin", hash_password("admin123"), "admin"),
            )


def create_user(username: str, password: str, role: str) -> int:
    username = username.strip()
    role = role.strip().lower()

    if not username:
        raise ValueError("Nom d'utilisateur requis")
    if len(password) < 4:
        raise ValueError("Le mot de passe doit contenir au moins 4 caractères")
    if role not in VALID_ROLES:
        raise ValueError("Rôle invalide")

    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO users(username, password_hash, role) VALUES(?, ?, ?)",
            (username, hash_password(password), role),
        )
        return cur.lastrowid


def list_users() -> list[dict]:
    with db_cursor() as cur:
        cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id ASC")
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def authenticate(username: str, password: str) -> User | None:
    pwd_hash = hash_password(password)
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?",
            (username, pwd_hash),
        )
        row = cur.fetchone()
    if row is None:
        return None
    return User(id=row["id"], username=row["username"], role=row["role"])
