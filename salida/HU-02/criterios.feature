# language: es
Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  para encontrar rápido a una persona

  Escenario: Ver el directorio completo con los datos principales de cada empleado
    Dado que existe el empleado "EMP-0001" con nombre "Ana López", puesto "Analista de Nómina", departamento "Recursos Humanos" y estado "activo"
    Y existe el empleado "EMP-0002" con nombre "Carlos Ruiz", puesto "Desarrollador", departamento "Tecnología" y estado "activo"
    Cuando abro el directorio de empleados
    Entonces veo el número de empleado, nombre, puesto, departamento y estado de "EMP-0001" y "EMP-0002"

  Escenario: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "EMP-0003" con nombre "María Fernández", correo "maria.fernandez@empresa.com" y departamento "Ventas"
    Cuando busco en el directorio el texto "maría fernández"
    Entonces veo en los resultados al empleado "EMP-0003" con nombre "María Fernández"

  Escenario: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "EMP-0004" con nombre "Jorge Pérez" y correo "jorge.perez@empresa.com"
    Cuando busco en el directorio el texto "JORGE.PEREZ@EMPRESA.COM"
    Entonces veo en los resultados al empleado "EMP-0004" con correo "jorge.perez@empresa.com"

  Escenario: Filtrar el directorio por departamento
    Dado que existe el empleado "EMP-0005" con nombre "Lucía Gómez" y departamento "Finanzas"
    Y existe el empleado "EMP-0006" con nombre "Pedro Sánchez" y departamento "Operaciones"
    Cuando filtro el directorio por el departamento "Finanzas"
    Entonces veo en los resultados al empleado "EMP-0005"
    Y no veo en los resultados al empleado "EMP-0006"

  Escenario: Buscar un empleado que no existe en el directorio
    Dado que existen empleados registrados en el directorio
    Cuando busco en el directorio el texto "xyz-sin-coincidencias"
    Entonces veo el mensaje "No se encontraron resultados"

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe el empleado "EMP-0007" con nombre "Rosa Jiménez", departamento "Tecnología" y estado "baja" desde la fecha "2024-03-01"
    Cuando abro el directorio de empleados
    Entonces veo en los resultados al empleado "EMP-0007" con estado "baja"
