# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registro exitoso de un empleado con datos válidos
    Dado que no existe ningún empleado con correo "ana.lopez@empresa.com"
    Y el último número de empleado asignado es "EMP-0007"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | Ana López              |
      | correo        | Ana.Lopez@Empresa.com   |
      | puesto        | Analista de Nómina     |
      | departamento  | Recursos Humanos       |
      | fecha_ingreso | 2024-01-10              |
    Entonces el sistema responde con código 201
    Y el empleado se guarda con correo "ana.lopez@empresa.com" en minúsculas
    Y el empleado se guarda con estado "activo"
    Y la pantalla muestra el mensaje de confirmación "Empleado EMP-0008 registrado con éxito"

  Escenario: Error al registrar con un correo ya registrado
    Dado que ya existe un empleado con correo "ana.lopez@empresa.com"
    Cuando registro un empleado con correo "ANA.LOPEZ@EMPRESA.COM"
    Entonces el sistema responde con código 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"

  Escenario: Error al registrar con un correo que no es corporativo
    Dado que no existe ningún empleado con correo "carlos.ruiz@gmail.com"
    Cuando registro un empleado con correo "carlos.ruiz@gmail.com"
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"

  Escenario: Error al registrar con un nombre demasiado corto
    Dado que no existe ningún empleado con correo "nuevo.empleado@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | A                            |
      | correo        | nuevo.empleado@empresa.com  |
      | puesto        | Analista de Nómina          |
      | departamento  | Recursos Humanos            |
      | fecha_ingreso | 2024-01-10                   |
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "nombre" debe corregirse

  Escenario: Error al registrar sin puesto
    Dado que no existe ningún empleado con correo "nuevo.empleado@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | Mario Pérez                 |
      | correo        | nuevo.empleado@empresa.com  |
      | puesto        |                              |
      | departamento  | Recursos Humanos            |
      | fecha_ingreso | 2024-01-10                   |
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "puesto" debe corregirse

  Escenario: Error al registrar con un departamento que no existe en el catálogo
    Dado que no existe ningún empleado con correo "nuevo.empleado@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | Mario Pérez                 |
      | correo        | nuevo.empleado@empresa.com  |
      | puesto        | Analista de Nómina          |
      | departamento  | Marketing                   |
      | fecha_ingreso | 2024-01-10                   |
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "departamento" debe corregirse

  Escenario: Error al registrar sin fecha de ingreso
    Dado que no existe ningún empleado con correo "nuevo.empleado@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | Mario Pérez                 |
      | correo        | nuevo.empleado@empresa.com  |
      | puesto        | Analista de Nómina          |
      | departamento  | Recursos Humanos            |
      | fecha_ingreso |                              |
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "fecha_ingreso" debe corregirse

  Escenario: Error al registrar con una fecha de ingreso futura
    Dado que la fecha actual del sistema es "2024-06-01"
    Y que no existe ningún empleado con correo "nuevo.empleado@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | Mario Pérez                 |
      | correo        | nuevo.empleado@empresa.com  |
      | puesto        | Analista de Nómina          |
      | departamento  | Recursos Humanos            |
      | fecha_ingreso | 2024-06-02                   |
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"

# Preguntas abiertas
# - No se especifica el formato exacto del mensaje de confirmación tras guardar
#   (se asumió "Empleado {numero_empleado} registrado con éxito"); confirmar texto exacto con el PO.
# - No se especifica el nombre exacto del campo o estructura que indica "qué campo corregir"
#   en la respuesta 422 de la regla 3; se asumió un identificador de campo (ej. "nombre", "puesto").
