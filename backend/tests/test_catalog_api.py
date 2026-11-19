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

    def create_product(
        self,
        *,
        name: str | None = None,
        price: str = "199.99",
        stock: int = 3,
        category_id: int | None = None,
        is_active: bool = True,
    ) -> dict:
        response = self.client.post(
            "/api/v1/products",
            json={
                "name": name or f"Test product {uuid4().hex[:8]}",
                "description": "Temporary integration-test product",
                "price": price,
                "stock": stock,
                "category_id": category_id,
                "image_url": None,
                "is_active": is_active,
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
        product = self.create_product(category_id=category["id"])

        self.assertEqual(product["category_id"], category["id"])
        self.assertIsNone(product["image_url"])
        self.assertTrue(product["is_active"])

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
        self.assertIsInstance(products_response.json()["items"], list)
        self.assertIn("total", products_response.json())
        self.assertIn("pages", products_response.json())

    def test_product_details_and_missing_product(self) -> None:
        products_response = self.client.get("/api/v1/products")
        self.assertEqual(products_response.status_code, 200)
        products = products_response.json()["items"]
        self.assertTrue(products)

        details_response = self.client.get(
            f"/api/v1/products/{products[0]['id']}"
        )
        missing_response = self.client.get("/api/v1/products/2147483647")

        self.assertEqual(details_response.status_code, 200)
        self.assertEqual(details_response.json()["id"], products[0]["id"])
        self.assertEqual(missing_response.status_code, 404)

    def test_product_filters_sorting_and_pagination(self) -> None:
        category = self.create_category()
        suffix = uuid4().hex[:8]
        cheaper = self.create_product(
            name=f"Search {suffix} Alpha",
            price="25.00",
            category_id=category["id"],
        )
        expensive = self.create_product(
            name=f"Search {suffix} Beta",
            price="75.00",
            category_id=category["id"],
        )
        self.create_product(
            name=f"Unrelated {uuid4().hex[:8]}",
            price="50.00",
        )

        first_page = self.client.get(
            "/api/v1/products",
            params={
                "query": suffix,
                "category_id": category["id"],
                "min_price": "20.00",
                "max_price": "80.00",
                "sort": "price_desc",
                "page": 1,
                "page_size": 1,
            },
        )
        self.assertEqual(first_page.status_code, 200, first_page.text)
        first_payload = first_page.json()
        self.assertEqual(first_payload["total"], 2)
        self.assertEqual(first_payload["pages"], 2)
        self.assertEqual(first_payload["items"][0]["id"], expensive["id"])

        second_page = self.client.get(
            "/api/v1/products",
            params={
                "query": suffix,
                "sort": "price_desc",
                "page": 2,
                "page_size": 1,
            },
        )
        self.assertEqual(second_page.status_code, 200, second_page.text)
        self.assertEqual(second_page.json()["items"][0]["id"], cheaper["id"])

        invalid_range = self.client.get(
            "/api/v1/products",
            params={"min_price": "100.00", "max_price": "10.00"},
        )
        self.assertEqual(invalid_range.status_code, 422, invalid_range.text)

    def test_admin_can_update_and_hide_product(self) -> None:
        product = self.create_product()

        response = self.client.patch(
            f"/api/v1/products/{product['id']}",
            json={
                "name": "  Updated product  ",
                "price": "349.50",
                "stock": 7,
                "image_url": "  https://example.com/product.jpg  ",
                "is_active": False,
            },
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 200, response.text)
        updated = response.json()
        self.assertEqual(updated["name"], "Updated product")
        self.assertEqual(updated["stock"], 7)
        self.assertEqual(updated["image_url"], "https://example.com/product.jpg")
        self.assertFalse(updated["is_active"])

        details_response = self.client.get(
            f"/api/v1/products/{product['id']}"
        )
        list_response = self.client.get(
            "/api/v1/products",
            params={"query": "Updated product"},
        )
        self.assertEqual(details_response.status_code, 404, details_response.text)
        self.assertEqual(list_response.json()["total"], 0)

    def test_product_update_validates_nulls_and_category(self) -> None:
        product = self.create_product()

        null_response = self.client.patch(
            f"/api/v1/products/{product['id']}",
            json={"price": None},
            headers=self.admin_headers,
        )
        category_response = self.client.patch(
            f"/api/v1/products/{product['id']}",
            json={"category_id": 2_147_483_647},
            headers=self.admin_headers,
        )

        self.assertEqual(null_response.status_code, 422, null_response.text)
        self.assertEqual(category_response.status_code, 404, category_response.text)
