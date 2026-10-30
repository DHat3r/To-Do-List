from datetime import datetime, timezone
from itertools import count

from fastapi import APIRouter, HTTPException, status
from app.schemas import TaskCreate, Task, TaskUpdate

# Un APIRouter es un "mini app": agrupa endpoints con un prefijo común.
# Todas las rutas de este archivo empiezan con /tasks.
router = APIRouter(prefix="/tasks", tags=["Tasks"])


# "Base de datos" en memoria: un dict de id -> Task.
# Se borra al reiniciar el servidor. En el paso 4 la cambiamos por SQLite.
# El guion bajo inicial indica que es privado de este módulo.

_tasks: dict[int, Task] = {}

# count(1) entrega 1, 2, 3... cada vez que llamas next(). Es un autoincremento.

_ids = count(start=1)


def _get_or_404(task_id: int) -> Task:
    """Busca una tarea; si no existe, corta la petición con un 404."""
    task = _tasks.get(task_id)  # .get() devuelve None si no existe, sin error
    if task is None:
        # raise HTTPException detiene el endpoint y FastAPI responde
        # {"detail": "Tarea no encontrada"} con código 404.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return task

@router.get("")
def list_tasks() -> list[Task]:
    return list(_tasks.values())

# status_code=201 Created es el código correcto al crear un recurso (no 200).
@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    # FastAPI ve que "data" es un modelo Pydantic: lee el JSON del body,
    # lo valida y te entrega un objeto TaskCreate ya revisado.
    task = Task(
        id=next(_ids),
        created_at=datetime.now(timezone.utc),  # guarda siempre la hora en UTC
        **data.model_dump(),  # model_dump() -> dict; ** lo expande como argumentos
    )
    _tasks[task.id] = task
    return task

# {task_id} es un parámetro de ruta. Por el type hint int, FastAPI convierte
# "/tasks/3" en task_id=3, y "/tasks/abc" responde 422 solo.

@router.get("/{task_id}")
def read_task(task_id: int) -> Task:
    return _get_or_404(task_id)

@router.patch("/{task_id}")
# exclude_unset=True: solo los campos que el cliente ENVIÓ.
    # Sin esto, los que no mandó llegarían como None y borrarían datos
def update_task(task_id:int, data: TaskUpdate) -> Task:
    task = _get_or_404(task_id)
    changes = data.model_dump(exclude_unset=True)
    updated = task.model_copy(update=changes)  # copia de la tarea con los cambios
    _tasks[task_id] = updated
    return updated

# 204 No Content: se borró bien y no hay nada que devolver.
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    _get_or_404(task_id)
    del _tasks[task_id]