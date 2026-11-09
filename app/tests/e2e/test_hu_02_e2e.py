"""Pruebas end-to-end para HU-02: consulta del directorio de empleados."""
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import httpx
from playwright.sync_api import expect

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
    así que la precondición de CP-12 se crea escribiendo directamente en la
    base de datos SQLite que usa el backend.
    """
    numero_empleado = f"EMP-TEST-{uuid.uuid4().hex[:8]}"
    correo = _correo_unico("baja")
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    try:
        cursor = conexion.execute(
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
        id_empleado = cursor.lastrowid
    finally:
        conexion.close()
    return {"id": id_empleado, "numero_empleado": numero_empleado, "correo": correo}


def test_cp_02_directorio_completo(page, url_web, url_api):
    """CP-02: ver el directorio completo con los datos principales de cada empleado."""
    ana = _crear_empleado(url_api, "Ana López", "Analista de Nómina", "Recursos Humanos")
    carlos = _crear_empleado(url_api, "Carlos Ruiz", "Desarrollador", "Tecnología")

    page.goto(url_web)
    page.get_by_test_id("tabla-empleados").wait_for()

    page.get_by_test_id(f"fila-empleado-{ana['id']}").wait_for()
    expect(page.get_by_test_id(f"numero-empleado-{ana['id']}")).to_have_text(ana["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{ana['id']}")).to_have_text("Activo")

    page.get_by_test_id(f"fila-empleado-{carlos['id']}").wait_for()
    expect(page.get_by_test_id(f"numero-empleado-{carlos['id']}")).to_have_text(carlos["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{carlos['id']}")).to_have_text("Activo")


def test_cp_04_busqueda_por_nombre(page, url_web, url_api):
    """CP-04: buscar un empleado por nombre sin distinguir mayúsculas de minúsculas."""
    maria = _crear_empleado(url_api, "María Fernández", "Ejecutiva de Ventas", "Ventas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill("maría fernández")

    page.get_by_test_id(f"fila-empleado-{maria['id']}").wait_for()


def test_cp_06_busqueda_por_correo(page, url_web, url_api):
    """CP-06: buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    jorge = _crear_empleado(url_api, "Jorge Pérez", "Contador", "Finanzas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(jorge["correo"].upper())

    page.get_by_test_id(f"fila-empleado-{jorge['id']}").wait_for()


def test_cp_08_filtrar_por_departamento(page, url_web, url_api):
    """CP-08: filtrar el directorio por departamento."""
    lucia = _crear_empleado(url_api, "Lucía Gómez", "Analista Financiero", "Finanzas")
    pedro = _crear_empleado(url_api, "Pedro Sánchez", "Supervisor", "Operaciones")

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option("Finanzas")

    page.get_by_test_id(f"fila-empleado-{lucia['id']}").wait_for()
    assert page.get_by_test_id(f"fila-empleado-{pedro['id']}").count() == 0


def test_cp_10_busqueda_sin_resultados(page, url_web, url_api):
    """CP-10: buscar un empleado que no existe en el directorio."""
    _crear_empleado(url_api, "Empleado Existente", "Puesto de prueba", "Tecnología")
    texto = f"xyz-sin-coincidencias-{uuid.uuid4().hex[:8]}"

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(texto)

    expect(page.get_by_test_id("sin-resultados")).to_have_text("No se encontraron resultados")


def test_cp_12_empleado_de_baja_en_el_directorio(page, url_web, url_api):
    """CP-12: un empleado dado de baja sigue apareciendo en el directorio."""
    rosa = _insertar_empleado_baja("Rosa Jiménez", "Tecnología", "2024-03-01")

    page.goto(url_web)

    page.get_by_test_id(f"fila-empleado-{rosa['id']}").wait_for()
    expect(page.get_by_test_id(f"estado-empleado-{rosa['id']}")).to_have_text("Baja")
