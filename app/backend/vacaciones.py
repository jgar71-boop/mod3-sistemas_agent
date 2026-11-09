"""Reglas de negocio para solicitar vacaciones (HU-10)."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

import modelos
from catalogos import FESTIVOS

TOPE_ANUAL = 12


def calcular_aniversario(fecha_ingreso: date) -> date:
    """Primer día en que el empleado cumple un año de antigüedad."""
    anio = fecha_ingreso.year + 1
    try:
        return date(anio, fecha_ingreso.month, fecha_ingreso.day)
    except ValueError:
        # 29 de febrero en un año no bisiesto: el aniversario cae el 1 de marzo.
        return date(anio, 3, 1)


def calcular_dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    """Días de lunes a viernes entre dos fechas (incluyentes) que no son festivo."""
    festivos = FESTIVOS.get(fecha_inicio.year, set())
    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5 and actual not in festivos:
            dias += 1
        actual += timedelta(days=1)
    return dias


def dias_usados_en_anio(db: Session, empleado_id: int, anio: int) -> int:
    solicitudes = (
        db.query(modelos.Vacacion)
        .filter(
            modelos.Vacacion.empleado_id == empleado_id,
            modelos.Vacacion.fecha_inicio >= date(anio, 1, 1),
            modelos.Vacacion.fecha_inicio <= date(anio, 12, 31),
        )
        .all()
    )
    return sum(solicitud.dias_habiles for solicitud in solicitudes)
