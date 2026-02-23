import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import (
    authenticate,
    create_user,
    delete_user,
    ensure_default_admin,
    list_users,
)


class AuthServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db()
        ensure_default_admin()

    def test_create_user_and_authenticate(self) -> None:
        uid = create_user("cashier1", "pass1234", "caissier")
        self.assertGreater(uid, 0)

        user = authenticate("cashier1", "pass1234")
        self.assertIsNotNone(user)
        self.assertEqual(user.role, "caissier")

    def test_list_users_contains_admin(self) -> None:
        users = list_users()
        usernames = [u["username"] for u in users]
        self.assertIn("admin", usernames)

    def test_delete_user_removes_non_admin(self) -> None:
        uid = create_user("tempuser", "pass1234", "caissier")
        delete_user(uid)

        usernames = [u["username"] for u in list_users()]
        self.assertNotIn("tempuser", usernames)

    def test_delete_user_blocks_default_admin(self) -> None:
        admin = [u for u in list_users() if u["username"] == "admin"][0]
        with self.assertRaises(ValueError):
            delete_user(admin["id"])


if __name__ == "__main__":
    unittest.main()
