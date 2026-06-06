.PHONY: setup setup-admin setup-backend dev dev-backend dev-admin db-migrate db-revision db-reset seed

setup:
	py scripts/setup_project.py

setup-admin:
	py scripts/setup_project.py --only-admin

setup-backend:
	py scripts/setup_project.py --only-backend

dev-backend:
	cd backend && venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-admin:
	cd admin && npm run dev

dev:
	@echo "Para iniciar ambos servicios en Windows, se recomienda abrir dos terminales o usar 'npm run dev' si se configura un script concurrently."
	@echo "Iniciando backend en esta terminal..."
	$(MAKE) dev-backend

db-migrate:
	cd backend && venv\Scripts\alembic upgrade head

db-revision:
	cd backend && venv\Scripts\alembic revision --autogenerate -m "$(msg)"

db-reset:
	@echo "Restableciendo la base de datos..."
	cd backend && venv\Scripts\py -c "import sys; print('¿Está seguro de borrar la base de datos de desarrollo? (s/n)'); ans = sys.stdin.readline().strip(); sys.exit(0 if ans.lower() == 's' else 1)"
	cd backend && venv\Scripts\py -m app.db.reset_db

