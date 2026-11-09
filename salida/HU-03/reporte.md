# Reporte · HU-03

**Estado:** ESCALAR A UNA PERSONA
**Costo de agentes:** 2.23 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (13 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 9 failed, 16 passed, 3 warnings in 182.40s (0:03:02)
- Triage → desarrollador: Al enviar numero_empleado y correo junto con puesto, la API responde 422 en vez de ignorar esos campos no editables y procesar el resto, devolviendo 200 según el criterio de aceptación (Escenario: Intentar editar el número de empleado y el correo).
- Código corregido; redespliegue OK
- Pruebas E2E: 5 failed, 20 passed, 3 warnings in 153.28s (0:02:33)
- Triage → despliegue: Las 5 pruebas fallan por timeout esperando que elementos del directorio (filas de empleados) se vuelvan visibles, lo cual es consistente con que la aplicación/backend no está respondiendo (no hay error de aserción de contenido, sino ausencia total de respuesta de la UI al cargar datos). Esto sugiere que el servicio o contenedor de la aplicación no está disponible o caído, impidiendo que el frontend reciba y renderice los datos del directorio.
- Despliegue corregido
- Pruebas E2E: 5 failed, 20 passed, 3 warnings in 153.01s (0:02:33)

## Última ejecución de pruebas
```
5 failed, 20 passed, 3 warnings in 153.01s (0:02:33)
- tests.e2e.test_hu_02_e2e::test_cp_02_directorio_completo[chromium]
  playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_test_id("fila-empleado-EMP-0305") to be visible
- tests.e2e.test_hu_02_e2e::test_cp_04_busqueda_por_nombre[chromium]
  playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_test_id("fila-empleado-EMP-0307") to be visible
- tests.e2e.test_hu_02_e2e::test_cp_06_busqueda_por_correo[chromium]
  playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_test_id("fila-empleado-EMP-0308") to be visible
- tests.e2e.test_hu_02_e2e::test_cp_08_filtrar_por_departamento[chromium]
  playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_test_id("fila-empleado-EMP-0309") to be visible
- tests.e2e.test_hu_02_e2e::test_cp_12_empleado_de_baja_en_el_directorio[chromium]
  playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_test_id("fila-empleado-EMP-TEST-b41923a3") to be visible
```