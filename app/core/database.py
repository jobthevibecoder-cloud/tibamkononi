from sqlalchemy import create_engine
from sqlalchemy.orm import Session, DeclarativeBase
from app.config import settings
import os

# Use SQLite for HF Spaces (persistent in the space)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tiba_mkononi.db")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency injection for database sessions."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


def close_db():
    """Dispose engine."""
    engine.dispose()
