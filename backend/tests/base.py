import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import Base, get_db
from app.main import app


if settings.test_database_url == settings.database_url:
    raise RuntimeError("TEST_DATABASE_URL must differ from DATABASE_URL")

test_engine = create_engine(
    settings.test_database_url,
    pool_pre_ping=True,
)


class DatabaseApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=test_engine)
        cls.connection = test_engine.connect()
        cls.transaction = cls.connection.begin()

        def override_get_db():
            with Session(
                bind=cls.connection,
                join_transaction_mode="create_savepoint",
            ) as session:
                yield session

        app.dependency_overrides[get_db] = override_get_db
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client_context.__exit__(None, None, None)
        app.dependency_overrides.clear()
        cls.transaction.rollback()
        cls.connection.close()
        test_engine.dispose()
