"""Pruebas de API para HU-02: consulta del directorio de empleados."""
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import httpx

RUTA_BASE_DATOS = Path(__file__).resolve().parents[2] / "backend" / "datos" / "empleados.db"


def _correo_unico(base: str) -> str:
    return f"{base}.{uuid.uuid4().hex[:8]}@empresa.com"


def _crear_empleado(url_api, nombre, puesto, departamento, fecha_ingreso="2023-01-10"):
    datos = {
        "nombre": nombre,
        "correo": _correo_unico("empleado"),
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": fecha_ingreso,
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _insertar_empleado_baja(nombre: str, departamento: str, fecha_baja: str) -> dict:
    """Siembra directamente en la base de datos un empleado dado de baja.

    La API no expone (todavía) una operación para dar de baja a un empleado,
    así que la precondición de CP-11 se crea escribiendo directamente en la
    base de datos SQLite que usa el backend.
    """
    numero_empleado = f"EMP-TEST-{uuid.uuid4().hex[:8]}"
    correo = _correo_unico("baja")
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    try:
        conexion.execute(
            """
            INSERT INTO empleados
                (numero_empleado, nombre, correo, puesto, departamento,
                 fecha_ingreso, estado, fecha_baja, creado_en)
            VALUES (?, ?, ?, ?, ?, ?, 'baja', ?, ?)
            """,
            (
                numero_empleado,
                nombre,
                correo,
                "Puesto de prueba",
                departamento,
                "2020-01-01",
                fecha_baja,
                datetime.utcnow().isoformat(sep=" "),
            ),
        )
        conexion.commit()
    finally:
        conexion.close()
    return {"numero_empleado": numero_empleado, "correo": correo}


def test_cp_01_directorio_completo(url_api):
    """CP-01: ver el directorio completo con los datos principales de cada empleado."""
    ana = _crear_empleado(url_api, "Ana López", "Analista de Nómina", "Recursos Humanos")
    carlos = _crear_empleado(url_api, "Carlos Ruiz", "Desarrollador", "Tecnología")

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    empleados = {e["numero_empleado"]: e for e in respuesta.json()}

    encontrado = empleados[ana["numero_empleado"]]
    assert encontrado["nombre"] == "Ana López"
    assert encontrado["puesto"] == "Analista de Nómina"
    assert encontrado["departamento"] == "Recursos Humanos"
    assert encontrado["estado"] == "activo"

    encontrado = empleados[carlos["numero_empleado"]]
    assert encontrado["nombre"] == "Carlos Ruiz"
    assert encontrado["puesto"] == "Desarrollador"
    assert encontrado["departamento"] == "Tecnología"
    assert encontrado["estado"] == "activo"


def test_cp_03_busqueda_por_nombre_sin_distinguir_mayusculas(url_api):
    """CP-03: buscar un empleado por nombre sin distinguir mayúsculas de minúsculas."""
    _crear_empleado(url_api, "María Fernández", "Ejecutiva de Ventas", "Ventas")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": "maría fernández"})
    assert respuesta.status_code == 200
    nombres = [e["nombre"] for e in respuesta.json()]
    assert "María Fernández" in nombres


def test_cp_05_busqueda_por_correo_sin_distinguir_mayusculas(url_api):
    """CP-05: buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    jorge = _crear_empleado(url_api, "Jorge Pérez", "Contador", "Finanzas")

    respuesta = httpx.get(
        f"{url_api}/api/empleados", params={"busqueda": jorge["correo"].upper()}
    )
    assert respuesta.status_code == 200
    correos = [e["correo"] for e in respuesta.json()]
    assert jorge["correo"] in correos


def test_cp_07_filtrar_por_departamento(url_api):
    """CP-07: filtrar el directorio por departamento."""
    lucia = _crear_empleado(url_api, "Lucía Gómez", "Analista Financiero", "Finanzas")
    pedro = _crear_empleado(url_api, "Pedro Sánchez", "Supervisor", "Operaciones")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"departamento": "Finanzas"})
    assert respuesta.status_code == 200
    numeros = [e["numero_empleado"] for e in respuesta.json()]
    assert lucia["numero_empleado"] in numeros
    assert pedro["numero_empleado"] not in numeros


def test_cp_09_busqueda_sin_coincidencias(url_api):
    """CP-09: buscar un empleado que no existe en el directorio."""
    _crear_empleado(url_api, "Empleado Existente", "Puesto de prueba", "Tecnología")
    texto = f"xyz-sin-coincidencias-{uuid.uuid4().hex[:8]}"

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": texto})
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp_11_empleado_de_baja_sigue_en_el_directorio(url_api):
    """CP-11: un empleado dado de baja sigue apareciendo en el directorio."""
    rosa = _insertar_empleado_baja("Rosa Jiménez", "Tecnología", "2024-03-01")

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    empleados = {e["numero_empleado"]: e for e in respuesta.json()}

    encontrado = empleados[rosa["numero_empleado"]]
    assert encontrado["estado"] == "baja"
    assert encontrado["fecha_baja"] == "2024-03-01"
