from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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

    # Opcionales (puedes no enviarlos), pero si los envías no pueden ser null.
    # El validador solo corre para los campos que llegaron en el JSON.
    # description sí admite null: es la forma de borrarla.
    @field_validator("title", "completed")
    @classmethod
    def reject_null(cls, value: str | bool | None) -> str | bool | None:
        if value is None:
            # Un ValueError aquí se convierte en un 422 con este mensaje.
            raise ValueError("no puede ser null")
        return value


# Lo que la API DEVUELVE: los campos base más los que pone el servidor.


class Task(TaskBase):
    id: int
    completed: bool = False  # una tarea nueva empieza sin completar
    created_at: datetime


# Lo que el cliente envía para registrarse.
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


# Lo que la API devuelve de un usuario: NUNCA incluye la contraseña ni su hash.
class User(BaseModel):
    id: int
    username: str


# Respuesta del login. "bearer" es el tipo de token estándar de OAuth2:
# el cliente lo envía en el header  Authorization: Bearer <token>
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
