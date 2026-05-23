# Organization Structure API

API для управления организационной компании 

## Технологический стек
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Alembic (миграции)
- Docker / Docker Compose
- Pytest (тесты)

## Быстрый старт bash
git clone https://github.com/твой-логин/org-structure-api.git;
cd org-structure-api;
docker-compose up --build

## Документация
http://localhost:8000/docs

## Эндпоинты

**POST** `/departments/` — Создать подразделение

**GET** `/departments/{id}` — Получить подразделение с деревом

**PATCH** `/departments/{id}` — Обновить / переместить

**DELETE** `/departments/{id}` — Удалить (cascade / reassign)

**POST** `/departments/{id}/employees/` — Создать сотрудника

## Тесты
cd org-structure-api
docker-compose exec web pytest test_api.py -v -- проверка работы api
docker-compose exec web alembic upgrade head --миграция

№№ Требывания 
Docker Desktop

№№ Автор
**Леськов С.А.**

GITHUB:https://github.com/leskov-sa
