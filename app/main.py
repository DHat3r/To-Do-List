from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import auth, tasks


# lifespan: código que corre al arrancar (antes del yield) y al apagar (después).
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(
    title="To-Do List",
    description="A simple To-Do List API",
    version="1.0.0",
    lifespan=lifespan,
)

# Registra en la app todas las rutas del router (/tasks, /tasks/{id}...)
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
