from datetime import timedelta

from fastapi.testclient import TestClient

from app.security import create_access_token

USER = {"username": "leandro", "password": "clave-segura-123"}


def test_register_returns_201_without_password(anon_client: TestClient):
    response = anon_client.post("/auth/register", json=USER)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "leandro"
    # Ni la contraseña ni su hash deben salir nunca en una respuesta.
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_username_returns_409(anon_client: TestClient):
    anon_client.post("/auth/register", json=USER)

    response = anon_client.post("/auth/register", json=USER)

    assert response.status_code == 409


def test_register_short_password_returns_422(anon_client: TestClient):
    response = anon_client.post(
        "/auth/register", json={"username": "leandro", "password": "corta"}
    )

    assert response.status_code == 422


def test_login_returns_bearer_token(anon_client: TestClient):
    anon_client.post("/auth/register", json=USER)

    response = anon_client.post("/auth/token", data=USER)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401(anon_client: TestClient):
    anon_client.post("/auth/register", json=USER)

    response = anon_client.post(
        "/auth/token", data={"username": "leandro", "password": "incorrecta-123"}
    )

    assert response.status_code == 401


def test_tasks_without_token_returns_401(anon_client: TestClient):
    response = anon_client.get("/tasks")

    assert response.status_code == 401


def test_tasks_with_invalid_token_returns_401(anon_client: TestClient):
    response = anon_client.get(
        "/tasks", headers={"Authorization": "Bearer no-es-un-jwt"}
    )

    assert response.status_code == 401


def test_tasks_with_expired_token_returns_401(anon_client: TestClient, auth_headers):
    auth_headers()  # crea el usuario con id 1
    # Un token que venció hace un minuto.
    expired = create_access_token(user_id=1, expires_in=timedelta(minutes=-1))

    response = anon_client.get("/tasks", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_user_cannot_see_or_edit_tasks_of_another_user(
    anon_client: TestClient, auth_headers
):
    ana = auth_headers("ana")
    beto = auth_headers("beto")
    task = anon_client.post("/tasks", json={"title": "Privada"}, headers=ana).json()

    # Beto no la ve en su lista, ni puede leerla, editarla o borrarla.
    assert anon_client.get("/tasks", headers=beto).json() == []
    assert anon_client.get(f"/tasks/{task['id']}", headers=beto).status_code == 404
    patch = anon_client.patch(
        f"/tasks/{task['id']}", json={"completed": True}, headers=beto
    )
    assert patch.status_code == 404
    delete = anon_client.delete(f"/tasks/{task['id']}", headers=beto)
    assert delete.status_code == 404
    # Y la tarea de Ana sigue intacta.
    assert (
        anon_client.get(f"/tasks/{task['id']}", headers=ana).json()["completed"]
        is False
    )
