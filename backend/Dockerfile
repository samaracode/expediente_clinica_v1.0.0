# ==========================================================================
# Backend FastAPI — Expediente Clínico ZOE
# Imagen Debian slim: wkhtmltopdf (pdfkit) y psycopg2 necesitan libs del SO
# que son problemáticas en Alpine.
#
# Se fija a "bookworm" (Debian 12) a propósito: en "trixie" (Debian 13, el
# default actual de python:3.12-slim) wkhtmltopdf fue eliminado de los repos
# y apt-get falla con "no installation candidate".
# ==========================================================================
FROM python:3.12-slim-bookworm

# Evita prompts de apt y archivos .pyc; logs sin buffer para ver salida en vivo
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencias del sistema:
#   - wkhtmltopdf: requerido por pdfkit (recibos y exportación de expedientes)
#   - libpq5: runtime de PostgreSQL para psycopg2
#   - fuentes: para que los PDF rendericen texto correctamente
RUN apt-get update && apt-get install -y --no-install-recommends \
        wkhtmltopdf \
        libpq5 \
        fontconfig \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python primero para aprovechar la caché de capas
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Puerto expuesto (las plataformas suelen inyectar $PORT)
ENV PORT=8000
EXPOSE 8000

# Arranque: corre migraciones de Alembic y luego levanta la API.
# Si las migraciones fallan, el contenedor falla rápido (no arranca con BD inconsistente).
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
