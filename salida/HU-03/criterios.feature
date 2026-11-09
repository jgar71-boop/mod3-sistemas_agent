# language: es
Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  Quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  Para mantener el directorio al día sin perder el historial

  Escenario: Editar el puesto y el departamento de un empleado activo
    Dado que existe un empleado con número "EMP-0010", puesto "Analista", departamento "Ventas" y estado "activo"
    Cuando edito al empleado "EMP-0010" con puesto "Analista Senior" y departamento "Tecnología"
    Entonces la respuesta tiene el código 200
    Y el empleado "EMP-0010" muestra puesto "Analista Senior" y departamento "Tecnología"

  Escenario: Intentar editar el número de empleado y el correo
    Dado que existe un empleado con número "EMP-0011", correo "ana.lopez@empresa.com" y estado "activo"
    Cuando edito al empleado "EMP-0011" enviando numero_empleado "EMP-9999" y correo "nuevo@empresa.com" junto con puesto "Analista"
    Entonces la respuesta tiene el código 200
    Y el empleado "EMP-0011" conserva el número "EMP-0011" y el correo "ana.lopez@empresa.com"

  Escenario: Dar de baja a un empleado activo
    Dado que existe un empleado con número "EMP-0012", estado "activo" y fecha_ingreso "2022-01-10"
    Cuando doy de baja al empleado "EMP-0012" con fecha_baja "2024-05-15"
    Entonces la respuesta tiene el código 200
    Y el empleado "EMP-0012" muestra estado "baja" y fecha_baja "2024-05-15"
    Y el empleado "EMP-0012" sigue apareciendo en el directorio

  Escenario: Intentar dar de baja con una fecha de baja anterior a la fecha de ingreso
    Dado que existe un empleado con número "EMP-0013", estado "activo" y fecha_ingreso "2023-03-01"
    Cuando doy de baja al empleado "EMP-0013" con fecha_baja "2023-01-15"
    Entonces la respuesta tiene el código 422
    Y la pantalla muestra el campo "fecha_baja" para corregir

  Escenario: Intentar editar a un empleado dado de baja
    Dado que existe un empleado con número "EMP-0014" y estado "baja"
    Cuando edito al empleado "EMP-0014" con puesto "Coordinador"
    Entonces la respuesta tiene el código 409
    Y el mensaje es "No se puede editar a un empleado dado de baja"

  Escenario: Intentar editar con un puesto demasiado corto
    Dado que existe un empleado con número "EMP-0015", puesto "Analista" y estado "activo"
    Cuando edito al empleado "EMP-0015" con puesto "A"
    Entonces la respuesta tiene el código 422
    Y la pantalla muestra el campo "puesto" para corregir

  Escenario: Intentar editar con un departamento que no está en la lista permitida
    Dado que existe un empleado con número "EMP-0016", departamento "Ventas" y estado "activo"
    Cuando edito al empleado "EMP-0016" con departamento "Marketing"
    Entonces la respuesta tiene el código 422
    Y la pantalla muestra el campo "departamento" para corregir

# Preguntas abiertas
# - ¿Al intentar editar numero_empleado o correo, el sistema debe ignorar esos campos silenciosamente
#   (como se asumió en el escenario 2) o debe responder con un error explícito? Las reglas de negocio
#   no lo especifican, solo indican que no se editan.
# - ¿Cuál es el mensaje exacto que debe mostrar la pantalla cuando fecha_baja es anterior a fecha_ingreso?
#   Las reglas de negocio solo indican la restricción, no el texto del mensaje.
