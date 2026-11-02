from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


# Un fixture es "preparación reutilizable": cualquier test que pida un
# parámetro llamado "client" recibe lo que devuelve esta función.
@pytest.fixture
def client() -> Iterator[TestClient]:
    # Base de datos SQLite en memoria, nueva para cada test: rápida y sin
    # tocar tasks.db. StaticPool reutiliza una sola conexión; sin eso, cada
    # conexión nueva vería una base en memoria distinta (y vacía).
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    # dependency_overrides: donde la app pida get_session, FastAPI usa esta otra.
    app.dependency_overrides[get_session] = get_test_session
    yield TestClient(app)  # TestClient llama a la app directamente, sin red
    app.dependency_overrides.clear()  # deja la app como estaba
