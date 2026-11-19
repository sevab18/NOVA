import argparse

from app.database import SessionLocal
from app.users.models import UserRole
from app.users.repository import UserRepository


def promote_user(email: str) -> bool:
    normalized_email = email.strip().lower()

    with SessionLocal() as db:
        user = UserRepository(db).get_by_email(normalized_email)
        if user is None:
            return False

        user.role = UserRole.ADMIN
        db.commit()
        return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Promote an existing user to administrator",
    )
    parser.add_argument("email", help="Email of an existing registered user")
    args = parser.parse_args()

    if promote_user(args.email):
        print("User promoted to administrator")
    else:
        raise SystemExit("User was not found")


if __name__ == "__main__":
    main()
