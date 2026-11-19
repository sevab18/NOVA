from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password
from app.users.models import User, UserRole
from tests.base import DatabaseApiTestCase


class CatalogApiTests(DatabaseApiTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        with Session(
            bind=cls.connection,
            join_transaction_mode="create_savepoint",
        ) as session:
            admin = User(
                name="Catalog test admin",
                email=f"catalog-admin-{uuid4().hex}@example.com",
                password_hash=hash_password("CatalogAdminPassword123"),
                role=UserRole.ADMIN,
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
            admin_id = admin.id

        cls.admin_headers = {
            "Authorization": f"Bearer {create_access_token(admin_id)}"
        }

    def create_category(self) -> dict:
        suffix = uuid4().hex[:8]
        response = self.client.post(
            "/api/v1/categories",
            json={
                "name": f"Test category {suffix}",
                "description": "Temporary integration-test category",
            },
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_category_crud(self) -> None:
        category = self.create_category()

        response = self.client.get(f"/api/v1/categories/{category['id']}")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["name"], category["name"])

        response = self.client.patch(
            f"/api/v1/categories/{category['id']}",
            json={"description": "Updated description"},
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["description"], "Updated description")

        response = self.client.delete(
            f"/api/v1/categories/{category['id']}",
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 204, response.text)

        response = self.client.get(f"/api/v1/categories/{category['id']}")
        self.assertEqual(response.status_code, 404, response.text)

    def test_create_product_with_category(self) -> None:
        category = self.create_category()
        suffix = uuid4().hex[:8]

        response = self.client.post(
            "/api/v1/products",
            json={
                "name": f"Test product {suffix}",
                "description": "Temporary integration-test product",
                "price": "199.99",
                "stock": 3,
                "category_id": category["id"],
            },
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(response.json()["category_id"], category["id"])

    def test_create_product_with_unknown_category(self) -> None:
        response = self.client.post(
            "/api/v1/products",
            json={
                "name": "Invalid category product",
                "price": "10.00",
                "stock": 1,
                "category_id": 2_147_483_647,
            },
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 404, response.text)
        self.assertEqual(response.json()["detail"], "Category not found")

    def test_lists_are_available(self) -> None:
        categories_response = self.client.get("/api/v1/categories")
        products_response = self.client.get("/api/v1/products")

        self.assertEqual(categories_response.status_code, 200)
        self.assertEqual(products_response.status_code, 200)
        self.assertIsInstance(categories_response.json(), list)
        self.assertIsInstance(products_response.json(), list)

    def test_product_details_and_missing_product(self) -> None:
        products_response = self.client.get("/api/v1/products")
        self.assertEqual(products_response.status_code, 200)
        products = products_response.json()
        self.assertTrue(products)

        details_response = self.client.get(
            f"/api/v1/products/{products[0]['id']}"
        )
        missing_response = self.client.get("/api/v1/products/2147483647")

        self.assertEqual(details_response.status_code, 200)
        self.assertEqual(details_response.json()["id"], products[0]["id"])
        self.assertEqual(missing_response.status_code, 404)
