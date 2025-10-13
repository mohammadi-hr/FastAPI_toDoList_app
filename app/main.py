from fastapi import FastAPI
from app.api.routes import tasks

app = FastAPI(title="FastAPI Base Project", version="1.0.0")

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI base To_Do_List project!"}
