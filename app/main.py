from fastapi import FastAPI
from app.api.routes import tasks_route
from app.api.routes import users_route

app = FastAPI(title="FastAPI Base To_Do_List Project",
              version="1.0.0", summary="A Simple Task Management Application")

app.include_router(tasks_route.router, prefix="/tasks", tags=["Tasks"])
app.include_router(users_route.router, prefix="/users", tags=["Users"])


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI base To_Do_List project!"}
