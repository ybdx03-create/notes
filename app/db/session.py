from contextlib import contextmanager

from sqlmodel import SQLModel, Session, create_engine

from app.core.config import get_settings

_settings = get_settings()
engine = create_engine(str(_settings.database_url), echo=False, future=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session
