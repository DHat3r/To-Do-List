from fastapi import FastAPI
from app.routers import tasks

app = FastAPI(title="To-Do List", description="A simple To-Do List API", version="1.0.0")

# Registra en la app todas las rutas del router (/tasks, /tasks/{id}...)
app.include_router(tasks.router)

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:  
        return {"status": "ok"}
