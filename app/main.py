from fastapi import FastAPI

app = FastAPI(title="To-Do List", description="A simple To-Do List API", version="1.0.0")

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:  
        return {"status": "ok"}
