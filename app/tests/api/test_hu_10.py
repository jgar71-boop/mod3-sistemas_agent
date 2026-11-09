"""Pruebas de API para HU-10: solicitar vacaciones."""
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


def _dar_de_baja(url_api, numero_empleado, fecha_baja):
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{numero_empleado}/baja",
        json={"fecha_baja": fecha_baja},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _solicitar_vacaciones(url_api, empleado_id, fecha_inicio, fecha_fin):
    return httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp_01_solicitud_valida_descuenta_los_dias_habiles(url_api):
    """CP-01: una solicitud válida se registra y descuenta los días hábiles correspondientes."""
    empleado = _crear_empleado(url_api, "Empleado CP-01", "2024-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-06", "2026-07-10")
    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp_03_fines_de_semana_y_festivos_no_se_descuentan(url_api):
    """CP-03: los sábados, domingos y festivos dentro del periodo no se descuentan."""
    empleado = _crear_empleado(url_api, "Empleado CP-03", "2024-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-21", "2026-12-31")
    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4


def test_cp_04_rechazar_por_antiguedad_insuficiente(url_api):
    """CP-04: una solicitud con menos de un año de antigüedad se rechaza."""
    empleado = _crear_empleado(url_api, "Empleado CP-04", "2025-12-21")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-18", "2026-12-20")
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp_05_rechazar_solicitud_que_rebasa_los_dias_disponibles(url_api):
    """CP-05: una solicitud que rebasa los días disponibles del año se rechaza indicando cuántos quedan."""
    empleado = _crear_empleado(url_api, "Empleado CP-05", "2024-01-01")
    previa = _solicitar_vacaciones(url_api, empleado["id"], "2026-01-05", "2026-01-08")
    assert previa.status_code == 201, previa.text
    assert previa.json()["dias_habiles"] == 4

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-08-03", "2026-08-13")
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp_06_rechazar_periodo_sin_ningun_dia_habil(url_api):
    """CP-06: un periodo sin ningún día hábil se rechaza."""
    empleado = _crear_empleado(url_api, "Empleado CP-06", "2024-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-11", "2026-07-12")
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp_07_rechazar_fecha_fin_anterior_a_fecha_inicio(url_api):
    """CP-07: una fecha de fin anterior a la fecha de inicio se rechaza."""
    empleado = _crear_empleado(url_api, "Empleado CP-07", "2024-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-10", "2026-07-05")
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp_08_rechazar_periodo_que_cruza_de_un_anio_a_otro(url_api):
    """CP-08: un periodo que cruza de un año a otro se rechaza."""
    empleado = _crear_empleado(url_api, "Empleado CP-08", "2024-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-12-28", "2027-01-08")
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp_09_rechazar_anio_fuera_del_catalogo_de_festivos(url_api):
    """CP-09: un año fuera del catálogo de festivos se rechaza."""
    empleado = _crear_empleado(url_api, "Empleado CP-09", "2020-01-01")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2028-01-10", "2028-01-15")
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp_10_rechazar_empleado_que_no_existe(url_api):
    """CP-10: un empleado que no existe se rechaza."""
    respuesta = _solicitar_vacaciones(url_api, 999999999, "2026-07-06", "2026-07-10")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp_11_rechazar_empleado_dado_de_baja(url_api):
    """CP-11: un empleado dado de baja se rechaza."""
    empleado = _crear_empleado(url_api, "Empleado CP-11", "2020-01-01")
    _dar_de_baja(url_api, empleado["numero_empleado"], "2026-01-10")

    respuesta = _solicitar_vacaciones(url_api, empleado["id"], "2026-07-06", "2026-07-10")
    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )
