from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    # pool_pre_ping previene errores por conexiones inactivas rotas.
    # Imprescindible con Postgres serverless (Neon) que escala a cero:
    # tras inactividad la conexión TCP queda muerta y pre_ping la reabre.
    pool_pre_ping=True,
    # Recicla conexiones tras 5 min para no arrastrar sockets que Neon
    # ya cerró del lado del servidor durante el "scale to zero".
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
