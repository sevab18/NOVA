from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def create(
        self,
        name: str,
        email: str,
        encoded_password: str,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=encoded_password,
        )
        self.db.add(user)
        self.db.flush()
        return user
