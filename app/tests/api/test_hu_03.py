"""Pruebas de API para HU-03: edición y baja de empleados."""
import uuid

import httpx


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


def test_cp_01_editar_puesto_y_departamento(url_api):
    """CP-01: editar con éxito el puesto y el departamento de un empleado activo."""
    empleado = _crear_empleado(url_api, "Empleado CP-01", "Analista", "Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"puesto": "Analista Senior", "departamento": "Tecnología"},
    )
    assert respuesta.status_code == 200

    verificacion = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    assert verificacion.status_code == 200
    cuerpo = verificacion.json()
    assert cuerpo["puesto"] == "Analista Senior"
    assert cuerpo["departamento"] == "Tecnología"


def test_cp_03_no_modifica_numero_empleado_ni_correo(url_api):
    """CP-03: el número de empleado y el correo no se modifican al editar."""
    empleado = _crear_empleado(url_api, "Empleado CP-03", "Analista", "Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={
            "numero_empleado": "EMP-9999",
            "correo": "nuevo@empresa.com",
            "puesto": "Analista",
        },
    )
    assert respuesta.status_code == 200

    verificacion = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    assert verificacion.status_code == 200
    cuerpo = verificacion.json()
    assert cuerpo["numero_empleado"] == empleado["numero_empleado"]
    assert cuerpo["correo"] == empleado["correo"]


def test_cp_04_dar_de_baja_empleado_activo(url_api):
    """CP-04: dar de baja a un empleado activo con éxito."""
    empleado = _crear_empleado(
        url_api, "Empleado CP-04", "Analista", "Ventas", fecha_ingreso="2022-01-10"
    )

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/baja",
        json={"fecha_baja": "2024-05-15"},
    )
    assert respuesta.status_code == 200

    verificacion = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    assert verificacion.status_code == 200
    cuerpo = verificacion.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["fecha_baja"] == "2024-05-15"

    listado = httpx.get(f"{url_api}/api/empleados")
    assert listado.status_code == 200
    numeros = [e["numero_empleado"] for e in listado.json()]
    assert empleado["numero_empleado"] in numeros


def test_cp_06_error_fecha_baja_anterior_a_ingreso(url_api):
    """CP-06: dar de baja con una fecha_baja anterior a la fecha de ingreso responde 422."""
    empleado = _crear_empleado(
        url_api, "Empleado CP-06", "Analista", "Ventas", fecha_ingreso="2023-03-01"
    )

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/baja",
        json={"fecha_baja": "2023-01-15"},
    )
    assert respuesta.status_code == 422
    assert "fecha_baja" in respuesta.json()["detail"]


def test_cp_08_error_editar_empleado_dado_de_baja(url_api):
    """CP-08: no se puede editar a un empleado dado de baja."""
    empleado = _crear_empleado(url_api, "Empleado CP-08", "Analista", "Ventas")
    _dar_de_baja(url_api, empleado["numero_empleado"], "2024-01-20")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"puesto": "Coordinador"},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"


def test_cp_10_error_puesto_muy_corto(url_api):
    """CP-10: editar con un puesto demasiado corto responde 422."""
    empleado = _crear_empleado(url_api, "Empleado CP-10", "Analista", "Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"puesto": "A"},
    )
    assert respuesta.status_code == 422
    assert "puesto" in respuesta.json()["detail"]


def test_cp_12_error_departamento_no_permitido(url_api):
    """CP-12: editar con un departamento fuera del catálogo permitido responde 422."""
    empleado = _crear_empleado(url_api, "Empleado CP-12", "Analista", "Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"departamento": "Marketing"},
    )
    assert respuesta.status_code == 422
    assert "departamento" in respuesta.json()["detail"]
