from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import TaskRecord
from app.schemas import Task, TaskCreate, TaskUpdate

# Un APIRouter es un "mini app": agrupa endpoints con un prefijo común.
# Todas las rutas de este archivo empiezan con /tasks.
router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Inyección de dependencias: cada endpoint que declare "session: SessionDep"
# recibe una sesión abierta por get_session, sin crearla él mismo.
# Así los tests pueden reemplazar get_session por una base de datos de prueba.
SessionDep = Annotated[Session, Depends(get_session)]


def _get_or_404(session: Session, task_id: int) -> TaskRecord:
    """Busca una tarea; si no existe, corta la petición con un 404."""
    task = session.get(TaskRecord, task_id)  # busca por clave primaria
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    return task


@router.get("")
def list_tasks(session: SessionDep) -> list[Task]:
    # select() arma la consulta SQL: SELECT * FROM tasks ORDER BY id
    return session.exec(select(TaskRecord).order_by(TaskRecord.id)).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, session: SessionDep) -> Task:
    task = TaskRecord(**data.model_dump())
    session.add(task)  # la marca para insertar
    session.commit()  # ejecuta el INSERT y guarda en disco
    session.refresh(task)  # recarga la fila para obtener el id asignado
    return task


@router.get("/{task_id}")
def read_task(task_id: int, session: SessionDep) -> Task:
    return _get_or_404(session, task_id)


@router.patch("/{task_id}")
def update_task(task_id: int, data: TaskUpdate, session: SessionDep) -> Task:
    task = _get_or_404(session, task_id)
    # exclude_unset=True: solo los campos que el cliente ENVIÓ.
    task.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: SessionDep) -> None:
    task = _get_or_404(session, task_id)
    session.delete(task)
    session.commit()
