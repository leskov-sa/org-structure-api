from fastapi import FastAPI
from app.routers import departments, employees
from app.database import engine
from app import models

# Создаём таблицы в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API", description="API управления организацией", version="1.0.0")

app.include_router(departments.router)
app.include_router(employees.router)


@app.get("/")
def root():
    return {"message": "Run"}


@app.get("/health")
def health():
    return {"status": "ok"}