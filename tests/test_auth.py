import os
import unittest

from pharmacy_pos.config import DB_PATH
from pharmacy_pos.database import init_db
from pharmacy_pos.services.auth_service import authenticate, create_user, ensure_default_admin, list_users


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


if __name__ == "__main__":
    unittest.main()
