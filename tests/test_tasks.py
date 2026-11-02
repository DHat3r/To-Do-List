from fastapi.testclient import TestClient


# Helper: crear una tarea se repite en muchos tests.
def create_task(client: TestClient, title: str = "Comprar pan") -> dict:
    response = client.post("/tasks", json={"title": title})
    return response.json()


def test_health_returns_ok(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task_returns_201_and_the_task(client: TestClient):
    response = client.post("/tasks", json={"title": "Comprar pan"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Comprar pan"
    assert body["completed"] is False


def test_create_task_with_empty_title_returns_422(client: TestClient):
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_list_tasks_returns_all_created(client: TestClient):
    create_task(client, "Tarea 1")
    create_task(client, "Tarea 2")

    response = client.get("/tasks")

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Tarea 1", "Tarea 2"]


def test_get_missing_task_returns_404(client: TestClient):
    response = client.get("/tasks/99")

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarea no encontrada"}


def test_patch_changes_only_sent_fields(client: TestClient):
    task = create_task(client, "Estudiar")

    response = client.patch(f"/tasks/{task['id']}", json={"completed": True})

    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "Estudiar"


def test_delete_task_returns_204_and_removes_it(client: TestClient):
    task = create_task(client)

    response = client.delete(f"/tasks/{task['id']}")

    assert response.status_code == 204
    # Comprobar el efecto, no solo el código: la tarea ya no debe existir.
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_patch_with_null_title_returns_422(client: TestClient):
    task = create_task(client)

    response = client.patch(f"/tasks/{task['id']}", json={"title": None})

    assert response.status_code == 422


def test_patch_with_null_completed_returns_422(client: TestClient):
    task = create_task(client)

    response = client.patch(f"/tasks/{task['id']}", json={"completed": None})

    assert response.status_code == 422


def test_patch_with_null_description_clears_it(client: TestClient):
    created = client.post("/tasks", json={"title": "Pan", "description": "Integral"})
    task_id = created.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"description": None})

    assert response.status_code == 200
    assert response.json()["description"] is None
