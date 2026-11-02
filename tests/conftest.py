from itertools import count

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import tasks


# Un fixture es "preparación reutilizable": cualquier test que pida un
# parámetro llamado "client" recibe lo que devuelve esta función.
@pytest.fixture
def client() -> TestClient:
    # Cada test empieza desde cero: si no vaciamos la "base de datos",
    # las tareas de un test se filtran al siguiente.
    # (Atajo temporal: en el paso 4 se reemplaza por dependency_overrides.)
    tasks._tasks.clear()
    tasks._ids = count(start=1)
    # TestClient llama a la app directamente, sin levantar uvicorn ni red.
    return TestClient(app)
