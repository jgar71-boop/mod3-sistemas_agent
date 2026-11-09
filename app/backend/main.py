"""API de gestión de empleados."""
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

import modelos
import vacaciones as reglas_vacaciones
from catalogos import DEPARTAMENTOS
from catalogos import FESTIVOS
from database import Base, engine, obtener_db
from esquemas import (
    EmpleadoActualizar,
    EmpleadoBaja,
    EmpleadoCrear,
    EmpleadoRespuesta,
    VacacionCrear,
    VacacionRespuesta,
    VacacionSaldo,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError):
    primer_error = exc.errors()[0]
    mensaje = primer_error["msg"]
    if mensaje.startswith("Value error, "):
        mensaje = mensaje.removeprefix("Value error, ")
    else:
        campo = primer_error["loc"][-1]
        mensaje = f"El campo '{campo}' debe corregirse"
    return JSONResponse(status_code=422, content={"detail": mensaje})


@app.get("/api/salud")
def salud():
    return {"estado": "ok"}


@app.get("/api/departamentos")
def departamentos():
    return DEPARTAMENTOS


def _generar_numero_empleado(db: Session) -> str:
    total = db.query(func.count(modelos.Empleado.id)).scalar() or 0
    return f"EMP-{total + 1:04d}"


def _obtener_empleado(numero_empleado: str, db: Session) -> modelos.Empleado:
    empleado = (
        db.query(modelos.Empleado)
        .filter(modelos.Empleado.numero_empleado == numero_empleado)
        .first()
    )
    if not empleado:
        raise HTTPException(status_code=404, detail="El empleado no existe")
    return empleado


@app.get("/api/empleados", response_model=list[EmpleadoRespuesta])
def listar_empleados(
    busqueda: str | None = None,
    departamento: str | None = None,
    db: Session = Depends(obtener_db),
):
    consulta = db.query(modelos.Empleado)
    if busqueda:
        texto = f"%{busqueda.strip().lower()}%"
        consulta = consulta.filter(
            func.lower(modelos.Empleado.nombre).like(texto)
            | func.lower(modelos.Empleado.correo).like(texto)
        )
    if departamento:
        consulta = consulta.filter(modelos.Empleado.departamento == departamento)
    return consulta.order_by(modelos.Empleado.id).all()


@app.post("/api/empleados", response_model=EmpleadoRespuesta, status_code=201)
def crear_empleado(datos: EmpleadoCrear, db: Session = Depends(obtener_db)):
    existente = (
        db.query(modelos.Empleado)
        .filter(modelos.Empleado.correo == datos.correo)
        .first()
    )
    if existente:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    empleado = modelos.Empleado(
        numero_empleado=_generar_numero_empleado(db),
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@app.get("/api/empleados/{numero_empleado}", response_model=EmpleadoRespuesta)
def obtener_empleado(numero_empleado: str, db: Session = Depends(obtener_db)):
    return _obtener_empleado(numero_empleado, db)


@app.put("/api/empleados/{numero_empleado}", response_model=EmpleadoRespuesta)
def actualizar_empleado(
    numero_empleado: str, datos: EmpleadoActualizar, db: Session = Depends(obtener_db)
):
    empleado = _obtener_empleado(numero_empleado, db)
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409, detail="No se puede editar a un empleado dado de baja"
        )
    if datos.puesto is not None:
        empleado.puesto = datos.puesto
    if datos.departamento is not None:
        empleado.departamento = datos.departamento
    db.commit()
    db.refresh(empleado)
    return empleado


@app.put("/api/empleados/{numero_empleado}/baja", response_model=EmpleadoRespuesta)
def dar_de_baja_empleado(
    numero_empleado: str, datos: EmpleadoBaja, db: Session = Depends(obtener_db)
):
    empleado = _obtener_empleado(numero_empleado, db)
    if datos.fecha_baja < empleado.fecha_ingreso:
        raise HTTPException(
            status_code=422, detail="El campo 'fecha_baja' debe corregirse"
        )
    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    db.commit()
    db.refresh(empleado)
    return empleado


def _obtener_empleado_por_id(empleado_id: int, db: Session) -> modelos.Empleado:
    empleado = db.get(modelos.Empleado, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@app.post(
    "/api/empleados/{empleado_id}/vacaciones",
    response_model=VacacionRespuesta,
    status_code=201,
)
def solicitar_vacaciones(
    empleado_id: int, datos: VacacionCrear, db: Session = Depends(obtener_db)
):
    empleado = _obtener_empleado_por_id(empleado_id, db)
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )
    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )
    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )
    anio = datos.fecha_inicio.year
    if anio not in FESTIVOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )
    if datos.fecha_inicio < reglas_vacaciones.calcular_aniversario(empleado.fecha_ingreso):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )
    dias_habiles = reglas_vacaciones.calcular_dias_habiles(
        datos.fecha_inicio, datos.fecha_fin
    )
    if dias_habiles == 0:
        raise HTTPException(
            status_code=400, detail="El periodo no incluye días hábiles"
        )
    dias_usados = reglas_vacaciones.dias_usados_en_anio(db, empleado.id, anio)
    dias_disponibles = reglas_vacaciones.TOPE_ANUAL - dias_usados
    if dias_habiles > dias_disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {dias_disponibles} días hábiles"
            ),
        )

    vacacion = modelos.Vacacion(
        empleado_id=empleado.id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    db.add(vacacion)
    db.commit()
    db.refresh(vacacion)

    return VacacionRespuesta(
        id=vacacion.id,
        empleado_id=empleado.id,
        fecha_inicio=vacacion.fecha_inicio,
        fecha_fin=vacacion.fecha_fin,
        dias_habiles=dias_habiles,
        dias_restantes=dias_disponibles - dias_habiles,
    )


@app.get("/api/empleados/{empleado_id}/vacaciones", response_model=VacacionSaldo)
def saldo_vacaciones(
    empleado_id: int, anio: int | None = None, db: Session = Depends(obtener_db)
):
    empleado = _obtener_empleado_por_id(empleado_id, db)
    anio_consulta = anio or date.today().year
    solicitudes = (
        db.query(modelos.Vacacion)
        .filter(
            modelos.Vacacion.empleado_id == empleado.id,
            modelos.Vacacion.fecha_inicio >= date(anio_consulta, 1, 1),
            modelos.Vacacion.fecha_inicio <= date(anio_consulta, 12, 31),
        )
        .order_by(modelos.Vacacion.fecha_inicio)
        .all()
    )
    dias_usados = sum(solicitud.dias_habiles for solicitud in solicitudes)
    return VacacionSaldo(
        empleado_id=empleado.id,
        anio=anio_consulta,
        dias_usados=dias_usados,
        dias_disponibles=reglas_vacaciones.TOPE_ANUAL - dias_usados,
        solicitudes=solicitudes,
    )
