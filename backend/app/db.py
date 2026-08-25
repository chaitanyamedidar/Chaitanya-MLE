from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import subscription as _subscription  # noqa: F401
    from app.models import user as _user  # noqa: F401
    from app.services.auth import seed_demo_user

    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "subscriptions" in inspector.get_table_names():
        cols = {col["name"] for col in inspector.get_columns("subscriptions")}
        if "user_id" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE subscriptions ADD COLUMN user_id INTEGER"))

    db = SessionLocal()
    try:
        demo = seed_demo_user(db)
        db.execute(
            text("UPDATE subscriptions SET user_id = :uid WHERE user_id IS NULL"),
            {"uid": demo.id},
        )
        db.commit()
    finally:
        db.close()
