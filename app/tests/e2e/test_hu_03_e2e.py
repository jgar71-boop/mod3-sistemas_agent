"""Pruebas end-to-end para HU-03: edición y baja de empleados."""
import uuid

import httpx
from playwright.sync_api import expect


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


def _dar_de_baja(url_api, numero_empleado, fecha_baja):
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{numero_empleado}/baja",
        json={"fecha_baja": fecha_baja},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _forzar_seleccion_invalida(page, test_id, valor):
    """Inyecta una opción fuera del catálogo: el <select> solo ofrece los
    departamentos válidos y no admite texto libre."""
    page.eval_on_selector(
        f"[data-testid='{test_id}']",
        """(select, valor) => {
            let opcion = Array.from(select.options).find((o) => o.value === valor)
            if (!opcion) {
                opcion = document.createElement('option')
                opcion.value = valor
                opcion.text = valor
                select.appendChild(opcion)
            }
            select.value = valor
            select.dispatchEvent(new Event('change', { bubbles: true }))
        }""",
        valor,
    )


def test_cp_02_editar_puesto_y_departamento(page, url_web, url_api):
    """CP-02: editar con éxito el puesto y el departamento de un empleado activo."""
    empleado = _crear_empleado(url_api, "Empleado CP-02", "Analista", "Ventas")

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option("Tecnología")
    page.get_by_test_id("empleado-guardar").click()

    page.get_by_test_id("mensaje-exito").wait_for()

    page.reload()
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    assert page.get_by_test_id("empleado-puesto").input_value() == "Analista Senior"
    assert page.get_by_test_id("empleado-departamento").input_value() == "Tecnología"


def test_cp_05_dar_de_baja_empleado_activo(page, url_web, url_api):
    """CP-05: dar de baja a un empleado activo con éxito."""
    empleado = _crear_empleado(
        url_api, "Empleado CP-05", "Analista", "Ventas", fecha_ingreso="2022-01-10"
    )

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2024-05-15")
    page.get_by_test_id("confirmar-baja").click()

    page.get_by_test_id("mensaje-exito").wait_for()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
    page.get_by_test_id("tabla-empleados").wait_for()
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()


def test_cp_07_error_fecha_baja_anterior_a_ingreso(page, url_web, url_api):
    """CP-07: dar de baja con una fecha_baja anterior a la fecha de ingreso responde con error."""
    empleado = _crear_empleado(
        url_api, "Empleado CP-07", "Analista", "Ventas", fecha_ingreso="2023-03-01"
    )

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2023-01-15")
    page.get_by_test_id("confirmar-baja").click()

    page.get_by_test_id("mensaje-error").wait_for()
    assert page.get_by_test_id("empleado-fecha-baja").get_attribute("aria-invalid") == "true"


def test_cp_09_error_editar_empleado_dado_de_baja(page, url_web, url_api):
    """CP-09: no se puede editar a un empleado dado de baja."""
    empleado = _crear_empleado(url_api, "Empleado CP-09", "Analista", "Ventas")
    _dar_de_baja(url_api, empleado["numero_empleado"], "2024-01-20")

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("Coordinador")
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    mensaje.wait_for()
    assert mensaje.inner_text() == "No se puede editar a un empleado dado de baja"


def test_cp_11_error_puesto_muy_corto(page, url_web, url_api):
    """CP-11: editar con un puesto demasiado corto responde con mensaje de error."""
    empleado = _crear_empleado(url_api, "Empleado CP-11", "Analista", "Ventas")

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    page.get_by_test_id("mensaje-error").wait_for()
    assert page.get_by_test_id("empleado-puesto").get_attribute("aria-invalid") == "true"


def test_cp_13_error_departamento_no_permitido(page, url_web, url_api):
    """CP-13: editar con un departamento fuera del catálogo permitido responde con mensaje de error."""
    empleado = _crear_empleado(url_api, "Empleado CP-13", "Analista", "Ventas")

    page.goto(url_web)
    page.get_by_test_id(f"fila-empleado-{empleado['id']}").wait_for()
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    _forzar_seleccion_invalida(page, "empleado-departamento", "Marketing")
    page.get_by_test_id("empleado-guardar").click()

    page.get_by_test_id("mensaje-error").wait_for()
    assert page.get_by_test_id("empleado-departamento").get_attribute("aria-invalid") == "true"
