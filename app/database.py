import os
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

# La URL se lee de una variable de entorno para poder cambiarla sin tocar
# el código (por ejemplo en Docker). Si no existe, usa un archivo local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# El engine administra las conexiones a la base de datos; se crea una sola vez.
# check_same_thread=False: SQLite por defecto solo deja usar una conexión en el
# hilo que la creó, y FastAPI atiende las peticiones en varios hilos.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    """Crea las tablas que aún no existen (no borra ni modifica las existentes)."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Dependencia de FastAPI: abre una sesión por petición y la cierra al terminar."""
    with Session(engine) as session:
        yield session
