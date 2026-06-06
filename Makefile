.PHONY: setup setup-admin setup-backend dev dev-backend dev-admin db-migrate db-revision db-reset seed

# Cross-platform: detecta Windows vs Unix
ifeq ($(OS),Windows_NT)
    PYTHON   = venv\Scripts\python
    ALEMBIC  = venv\Scripts\alembic
    UVICORN  = venv\Scripts\uvicorn
    PY_SETUP = py
else
    PYTHON   = venv/bin/python
    ALEMBIC  = venv/bin/alembic
    UVICORN  = venv/bin/uvicorn
    PY_SETUP = python3
endif

setup:
	$(PY_SETUP) scripts/setup_project.py

setup-admin:
	$(PY_SETUP) scripts/setup_project.py --only-admin

setup-backend:
	$(PY_SETUP) scripts/setup_project.py --only-backend

dev-backend:
	cd backend && $(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8005

dev-admin:
	cd admin && npm run dev

dev:
	@echo "Abre dos terminales y corre 'make dev-backend' y 'make dev-admin' por separado."

db-migrate:
	cd backend && $(ALEMBIC) upgrade head

db-revision:
	cd backend && $(ALEMBIC) revision --autogenerate -m "$(msg)"

db-reset:
	cd backend && $(PYTHON) -m app.db.reset_db

seed:
	cd backend && $(PYTHON) -m app.db.seed
