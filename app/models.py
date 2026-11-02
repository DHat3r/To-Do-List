from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


# table=True convierte la clase en una tabla de la base de datos.
# Es distinta de los esquemas de schemas.py: esta clase describe cómo se
# GUARDA una tarea; los esquemas describen lo que ENTRA y SALE por la API.
class TaskRecord(SQLModel, table=True):
    __tablename__ = "tasks"

    # None al crear: la base de datos asigna el id (autoincremento).
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    completed: bool = False
    # default_factory se ejecuta en cada inserción; default=datetime.now(UTC)
    # se evaluaría una sola vez al importar y todas tendrían la misma fecha.
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
