from datetime import timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.users.models import User
from app.users.repository import UserRepository
from tests.base import DatabaseApiTestCase


class AuthApiTests(DatabaseApiTestCase):
    def user_data(self) -> dict[str, str]:
        suffix = uuid4().hex
        return {
            "name": "  Test User  ",
            "email": f"USER-{suffix}@EXAMPLE.COM",
            "password": "StrongTestPassword123",
        }

    def register_user(self) -> tuple[dict[str, str], dict]:
        data = self.user_data()
        response = self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(response.status_code, 201, response.text)
        return data, response.json()

    def login(self, email: str, password: str) -> str:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["token_type"], "bearer")
        return response.json()["access_token"]

    def test_register_normalizes_and_hashes_password(self) -> None:
        data, user_response = self.register_user()

        self.assertEqual(user_response["name"], "Test User")
        self.assertEqual(user_response["email"], data["email"].lower())
        self.assertEqual(user_response["role"], "customer")
        self.assertNotIn("password", user_response)
        self.assertNotIn("password_hash", user_response)

        with Session(
            bind=self.connection,
            join_transaction_mode="create_savepoint",
        ) as session:
            user = UserRepository(session).get_by_email(data["email"].lower())
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, data["password"])
            self.assertTrue(verify_password(data["password"], user.password_hash))

    def test_duplicate_email_returns_conflict(self) -> None:
        data, _ = self.register_user()
        data["email"] = data["email"].lower()

        response = self.client.post("/api/v1/auth/register", json=data)

        self.assertEqual(response.status_code, 409, response.text)

    def test_registration_validates_input(self) -> None:
        invalid_payloads = (
            {
                "name": "Test User",
                "email": "not-an-email",
                "password": "StrongTestPassword123",
            },
            {
                "name": "Test User",
                "email": f"short-{uuid4().hex}@example.com",
                "password": "short",
            },
            {
                "name": "   ",
                "email": f"blank-{uuid4().hex}@example.com",
                "password": "StrongTestPassword123",
            },
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/api/v1/auth/register",
                    json=payload,
                )
                self.assertEqual(response.status_code, 422, response.text)

    def test_login_and_current_profile(self) -> None:
        data, registered_user = self.register_user()
        token = self.login(data["email"], data["password"])

        response = self.client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["id"], registered_user["id"])
        self.assertEqual(response.json()["email"], data["email"].lower())

    def test_invalid_credentials_return_same_error(self) -> None:
        data, _ = self.register_user()

        for email, password in (
            (data["email"], "WrongPassword"),
            (f"missing-{uuid4().hex}@example.com", data["password"]),
        ):
            with self.subTest(email=email):
                response = self.client.post(
                    "/api/v1/auth/login",
                    json={"email": email, "password": password},
                )
                self.assertEqual(response.status_code, 401, response.text)
                self.assertEqual(
                    response.json()["detail"],
                    "Invalid email or password",
                )

    def test_invalid_and_expired_tokens_are_rejected(self) -> None:
        _, user_response = self.register_user()
        expired_token = create_access_token(
            user_response["id"],
            expires_delta=timedelta(seconds=-1),
        )

        for token in ("not-a-valid-token", expired_token):
            with self.subTest(token=token):
                response = self.client.get(
                    "/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"},
                )
                self.assertEqual(response.status_code, 401, response.text)

    def test_token_is_rejected_after_user_is_deleted(self) -> None:
        data, user_response = self.register_user()
        token = self.login(data["email"], data["password"])

        with Session(
            bind=self.connection,
            join_transaction_mode="create_savepoint",
        ) as session:
            user = session.get(User, user_response["id"])
            session.delete(user)
            session.commit()

        response = self.client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 401, response.text)

    def test_catalog_write_requires_admin(self) -> None:
        data, _ = self.register_user()
        customer_token = self.login(data["email"], data["password"])
        category_data = {"name": f"Protected {uuid4().hex[:8]}"}

        anonymous_response = self.client.post(
            "/api/v1/categories",
            json=category_data,
        )
        customer_response = self.client.post(
            "/api/v1/categories",
            json=category_data,
            headers={"Authorization": f"Bearer {customer_token}"},
        )

        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(customer_response.status_code, 403)

    def test_openapi_contains_versioned_auth_routes(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200, response.text)

        paths = response.json()["paths"]
        self.assertIn("/api/v1/auth/register", paths)
        self.assertIn("/api/v1/auth/login", paths)
        self.assertIn("/api/v1/users/me", paths)
