"""Esquemas Pydantic para la gestión de empleados."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

from catalogos import DEPARTAMENTOS


class EmpleadoCrear(BaseModel):
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not (2 <= len(valor.strip()) <= 80):
            raise ValueError("El campo 'nombre' debe corregirse")
        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        correo = valor.strip().lower()
        if not correo.endswith("@empresa.com"):
            raise ValueError("Usa el correo corporativo @empresa.com")
        return correo

    @field_validator("puesto")
    @classmethod
    def validar_puesto(cls, valor: str) -> str:
        if not (2 <= len(valor.strip()) <= 60):
            raise ValueError("El campo 'puesto' debe corregirse")
        return valor

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        if valor not in DEPARTAMENTOS:
            raise ValueError("El campo 'departamento' debe corregirse")
        return valor

    @field_validator("fecha_ingreso", mode="before")
    @classmethod
    def validar_fecha_ingreso_presente(cls, valor):
        if valor in (None, ""):
            raise ValueError("El campo 'fecha_ingreso' debe corregirse")
        return valor

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso_no_futura(cls, valor: date) -> date:
        if valor > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")
        return valor


class EmpleadoActualizar(BaseModel):
    puesto: str | None = None
    departamento: str | None = None

    @field_validator("puesto")
    @classmethod
    def validar_puesto(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        if not (2 <= len(valor.strip()) <= 60):
            raise ValueError("El campo 'puesto' debe corregirse")
        return valor

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str | None) -> str | None:
        if valor is None:
            return valor
        if valor not in DEPARTAMENTOS:
            raise ValueError("El campo 'departamento' debe corregirse")
        return valor


class EmpleadoBaja(BaseModel):
    fecha_baja: date

    @field_validator("fecha_baja", mode="before")
    @classmethod
    def validar_fecha_baja_presente(cls, valor):
        if valor in (None, ""):
            raise ValueError("El campo 'fecha_baja' debe corregirse")
        return valor


class EmpleadoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None
    creado_en: datetime


class VacacionCrear(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class VacacionRespuesta(BaseModel):
    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int
    dias_restantes: int


class VacacionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int


class VacacionSaldo(BaseModel):
    empleado_id: int
    anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: list[VacacionItem]
