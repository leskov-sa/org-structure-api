import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Organization Structure API is running"}


def test_create_department():
    response = client.post("/departments/", json={"name": "IT Department"})
    assert response.status_code == 200
    assert response.json()["name"] == "IT Department"


def test_create_department_duplicate():
    client.post("/departments/", json={"name": "Backend"})
    response = client.post("/departments/", json={"name": "Backend"})
    assert response.status_code == 400


def test_create_employee():
    dept = client.post("/departments/", json={"name": "HR"}).json()
    response = client.post(
        f"/departments/{dept['id']}/employees/",
        json={"full_name": "Иван Петров", "position": "Менеджер"}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Иван Петров"


def test_get_department():
    dept = client.post("/departments/", json={"name": "Test Dept"}).json()
    response = client.get(f"/departments/{dept['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Dept"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    