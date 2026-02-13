import hashlib
from dataclasses import dataclass

from pharmacy_pos.database import db_cursor


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
