"""Pruebas end-to-end para HU-10: solicitar vacaciones."""
import uuid

import httpx


def _correo_unico(base: str) -> str:
    return f"{base}.{uuid.uuid4().hex[:8]}@empresa.com"


def _crear_empleado(url_api, nombre, fecha_ingreso):
    datos = {
        "nombre": nombre,
        "correo": _correo_unico("empleado"),
        "puesto": "Analista",
        "departamento": "Ventas",
        "fecha_ingreso": fecha_ingreso,
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cp_02_solicitud_valida_descuenta_los_dias_habiles(page, url_web, url_api):
    """CP-02: una solicitud válida se registra y descuenta los días hábiles correspondientes."""
    empleado = _crear_empleado(url_api, "Empleado CP-02", "2024-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    mensaje.wait_for()
    assert (
        mensaje.inner_text()
        == "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    )
