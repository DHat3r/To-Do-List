from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select

from app.dependencies import CurrentUserDep, SessionDep
from app.models import TaskRecord, UserRecord
from app.schemas import Task, TaskCreate, TaskUpdate

# Un APIRouter es un "mini app": agrupa endpoints con un prefijo común.
# Todas las rutas de este archivo empiezan con /tasks.
router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _get_or_404(session: Session, task_id: int, user: UserRecord) -> TaskRecord:
    """Busca una tarea del usuario; si no existe o es de otro, corta con un 404."""
    task = session.get(TaskRecord, task_id)  # busca por clave primaria
    # 404 y no 403 si es de otro usuario: un 403 confirmaría que la tarea
    # existe, y eso ya es información que no le corresponde.
    if task is None or task.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada"
        )
    return task


@router.get("")
def list_tasks(session: SessionDep, user: CurrentUserDep) -> list[Task]:
    # SELECT * FROM tasks WHERE owner_id = ? ORDER BY id
    query = (
        select(TaskRecord).where(TaskRecord.owner_id == user.id).order_by(TaskRecord.id)
    )
    return session.exec(query).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, session: SessionDep, user: CurrentUserDep) -> Task:
    # El dueño sale del token, nunca del body: así nadie crea tareas a nombre de otro.
    task = TaskRecord(**data.model_dump(), owner_id=user.id)
    session.add(task)  # la marca para insertar
    session.commit()  # ejecuta el INSERT y guarda en disco
    session.refresh(task)  # recarga la fila para obtener el id asignado
    return task


@router.get("/{task_id}")
def read_task(task_id: int, session: SessionDep, user: CurrentUserDep) -> Task:
    return _get_or_404(session, task_id, user)


@router.patch("/{task_id}")
def update_task(
    task_id: int, data: TaskUpdate, session: SessionDep, user: CurrentUserDep
) -> Task:
    task = _get_or_404(session, task_id, user)
    # exclude_unset=True: solo los campos que el cliente ENVIÓ.
    task.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: SessionDep, user: CurrentUserDep) -> None:
    task = _get_or_404(session, task_id, user)
    session.delete(task)
    session.commit()
