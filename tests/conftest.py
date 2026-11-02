import os
from collections.abc import Callable, Iterator

# app.security exige SECRET_KEY al importarse, así que hay que definirla
# ANTES de importar la app. Es una clave falsa, solo para los tests.
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture
def anon_client() -> Iterator[TestClient]:
    """Cliente SIN token, con una base de datos en memoria nueva para cada test."""
    # StaticPool reutiliza una sola conexión; sin eso, cada conexión nueva
    # vería una base en memoria distinta (y vacía).
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


@pytest.fixture
def auth_headers(anon_client: TestClient) -> Callable[..., dict[str, str]]:
    """Fábrica: registra un usuario, hace login y devuelve el header con su token."""

    def _auth_headers(username: str = "leandro", password: str = "clave-segura-123"):
        anon_client.post(
            "/auth/register", json={"username": username, "password": password}
        )
        # El login es un formulario (data=), no JSON (json=), como pide OAuth2.
        response = anon_client.post(
            "/auth/token", data={"username": username, "password": password}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _auth_headers


@pytest.fixture
def client(anon_client: TestClient, auth_headers) -> TestClient:
    """Cliente con un usuario logueado: todas sus peticiones llevan el token."""
    anon_client.headers.update(auth_headers())
    return anon_client
