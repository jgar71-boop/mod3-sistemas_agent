 Lo siguientes son pasos de la fabrica workflow determinista o humano:

 - verificar y pruebas_e2e
 - pedir aclaracion y aprobar plan, pausas interrupt para una persona.
 - listo y fin/reporte. 
 
 Agentes (bucle modelo → herramientas → modelo):
   - analizar: Agente 1, analista (bucle de agentes/base.py).
   - disenar_casos: Agente 2, diseñador (bucle de agentes/base.py).
   - planificar y construir: Agente 3, desarrollador, con Claude Code. Planificar es de solo lectura; construir edita.
   - desplegar: Agente 4, despliegue. automatizar: Agente 5, automatizador. Los dos usan Claude Code y corren en paralelo.
   - corregir_codigo, corregir_pruebas y corregir_despliegue: los agentes 3, 5 y 4 de nuevo.

Agente: un modelo en bucle con herramientas, que decide qué hacer en cada paso (leer, escribir, ejecutar).

Workflow: el grafo de LangGraph en sí. Las decisiones de las aristas condicionales y los límites (MAX_INTENTOS, MAX_CICLOS, PRESUPUESTO_USD) los pone el código, no el modelo.

Las salidas se fueron validando dentro de reporte.md

Intervine en el workflow - pedir aclaracion y aprobar plan, pausas interrupt para una persona.

Donde atravez de validaciones y preguntas, yo como intermediario decido si detengo, ajusto o continuo con el flujo.

La fábrica usa un workflow orquestado por código: un grafo de estado de LangGraph. Los agentes trabajan dentro de nodos del grafo, pero no deciden el orden de ejecución. El grafo fija la secuencia, y los modelos solo intervienen en puntos concretos.

Aprobe el plan porque lo veia bien en un inicio, revise el archivo de criterios y coincidia pero vi que los mensajes no estaban correctos y fue porque no agregue los dos archivos de convenciones y reglas a los archivos de contexto solo los pegue a la ruta y paso lo siguiente:

El desarrollador no veia los festivos de 2026 - 2027 ni los mensajes de error exactos.

Se realizo el ajuste de meter reglas_vacaciones.md al final del archivo contexto/reglas_negocio.md y convenciones_vacaciones.md al final del archivo contexto/convenciones_app.md

Con esto se soluciono el problema y tambien se ajustaron los siguientes achivos ya que apuntaban a esas rutas y prodrian provocar confictos.

1. Hay una referencia que ya no aplica. En la sección agregada a convenciones_app.md, la línea 51 dice «Las reglas de negocio están en contexto/reglas_vacaciones.md». Cuando el desarrollador la lea en app/CLAUDE.md, buscará un archivo que no puede abrir. Claude las detecto y las corrigio.
2. Los archivos sueltos siguen en contexto/. reglas_vacaciones.md y convenciones_vacaciones.md siguen ahí, y el analista y el diseñador pueden leer las mismas reglas dos veces. Claude las detecto y las corrigio.

Un detalle pendiente: la historia historias/HU-10-solicitar-vacaciones.md, en las líneas 13, 14 y 28, todavía dice que el detalle está en contexto/reglas_vacaciones.md y contexto/convenciones_vacaciones.md. No la toqué porque es el material de entrada que te dio el profesor. Si el analista intenta abrir esos archivos, recibirá un error de «no existe» como texto y podrá corregir el rumbo: su prompt ya le dice que lea contexto/reglas_negocio.md, donde ahora está todo. Si prefieres evitar ese tropiezo, puedo cambiar esas tres líneas para que apunten a reglas_negocio.md y convenciones_app.md.

Y con esto el aplicacion cumplio con los requisitos solicitados.



 