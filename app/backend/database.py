"""Configuración de la base de datos SQLite para la gestión de empleados."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DIRECTORIO_DATOS = Path(__file__).resolve().parent / "datos"
DIRECTORIO_DATOS.mkdir(exist_ok=True)
RUTA_BASE_DATOS = DIRECTORIO_DATOS / "empleados.db"

engine = create_engine(
    f"sqlite:///{RUTA_BASE_DATOS}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
