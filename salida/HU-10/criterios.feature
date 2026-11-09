# language: es

Característica: Solicitar vacaciones
  Como empleado de la empresa
  quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Una solicitud válida se registra y descuenta los días hábiles correspondientes
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Y el empleado no tiene días de vacaciones usados en el año 2026
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 201
    Y el cuerpo de la respuesta tiene "dias_habiles" igual a 5
    Y el cuerpo de la respuesta tiene "dias_restantes" igual a 7
    Y en pantalla "vacaciones-mensaje" muestra "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Y el empleado no tiene días de vacaciones usados en el año 2026
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2026-12-21" y fecha_fin "2026-12-31"
    Entonces la respuesta tiene código 201
    Y el cuerpo de la respuesta tiene "dias_habiles" igual a 8
    Y el cuerpo de la respuesta tiene "dias_restantes" igual a 4

  Escenario: Una solicitud con menos de un año de antigüedad se rechaza
    Dado que existe un empleado activo con id 10, numero_empleado "EMP-0010" y fecha_ingreso "2025-12-21"
    Cuando se envía POST /api/empleados/10/vacaciones con fecha_inicio "2026-12-18" y fecha_fin "2026-12-20"
    Entonces la respuesta tiene código 400
    Y el cuerpo de la respuesta tiene "detail" igual a "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Una solicitud que rebasa los días disponibles del año se rechaza indicando cuántos quedan
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Y el empleado ya tiene 4 días hábiles usados en el año 2026
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2026-08-03" y fecha_fin "2026-08-13"
    Entonces la respuesta tiene código 400
    Y el cuerpo de la respuesta tiene "detail" igual a "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Un periodo sin ningún día hábil se rechaza
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2026-07-11" y fecha_fin "2026-07-12"
    Entonces la respuesta tiene código 400
    Y el cuerpo de la respuesta tiene "detail" igual a "El periodo no incluye días hábiles"

  Escenario: Una fecha de fin anterior a la fecha de inicio se rechaza
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2026-07-10" y fecha_fin "2026-07-05"
    Entonces la respuesta tiene código 400
    Y el cuerpo de la respuesta tiene "detail" igual a "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Un periodo que cruza de un año a otro se rechaza
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2026-12-28" y fecha_fin "2027-01-08"
    Entonces la respuesta tiene código 400
    Y el cuerpo de la respuesta tiene "detail" igual a "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Un año fuera del catálogo de festivos se rechaza
    Dado que existe un empleado activo con id 7, numero_empleado "EMP-0007" y fecha_ingreso "2024-01-01"
    Cuando se envía POST /api/empleados/7/vacaciones con fecha_inicio "2028-01-10" y fecha_fin "2028-01-15"
    Entonces la respuesta tiene código 400
    Y el cuerpo de la respuesta tiene "detail" igual a "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Un empleado que no existe se rechaza
    Dado que no existe ningún empleado con id 9999
    Cuando se envía POST /api/empleados/9999/vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 404
    Y el cuerpo de la respuesta tiene "detail" igual a "Empleado no encontrado"

  Escenario: Un empleado dado de baja se rechaza
    Dado que existe un empleado con id 8, numero_empleado "EMP-0008", fecha_ingreso "2020-01-01", estado "baja" y fecha_baja "2026-01-10"
    Cuando se envía POST /api/empleados/8/vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la respuesta tiene código 409
    Y el cuerpo de la respuesta tiene "detail" igual a "No se pueden solicitar vacaciones para un empleado dado de baja"

# Preguntas abiertas
# Ninguna: las reglas de negocio, los mensajes de error exactos, el formato de la API
# y los festivos de 2026-2027 quedaron completamente definidos en
# contexto/reglas_negocio.md y contexto/convenciones_app.md.
