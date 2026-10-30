from datetime import datetime
from pydantic import BaseModel, Field


# Campos que comparten "crear" y "leer". Evita repetirlos.
class TaskBase(BaseModel):
    # Field() agrega reglas de validación. Si llega un title vacío o de más
    # de 100 caracteres, FastAPI responde 422 solo, sin que escribas un if.
    title: str = Field(min_length=1, max_length=100)
    # "str | None" significa opcional: puede venir un texto o nada.
    description: str | None = Field(default=None, max_length=500)

# Lo que el cliente ENVÍA para crear una tarea. No trae id ni fecha:
# esos los decide el servidor, nunca el cliente.
class TaskCreate(TaskBase):
    pass

# Lo que el cliente envía para EDITAR. Todo es opcional, porque con PATCH
# solo mandas lo que quieres cambiar, por ejemplo {"completed": true}
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool | None = Field(default=None)

# Lo que la API DEVUELVE: los campos base más los que pone el servidor.

class Task(TaskBase):
    id: int
    completed: bool = False   # una tarea nueva empieza sin completar
    created_at: datetime

