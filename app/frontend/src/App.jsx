import { useEffect, useState } from 'react'
import './App.css'

const DATOS_INICIALES = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

function campoDesdeMensaje(mensaje) {
  const coincidencia = mensaje.match(/campo '([^']+)'/)
  if (coincidencia) return coincidencia[1]
  if (mensaje.includes('correo')) return 'correo'
  if (mensaje.includes('fecha de ingreso')) return 'fecha_ingreso'
  return null
}

function Directorio({ departamentos, recargarContador, onEditar, onBaja, onVacaciones }) {
  const [empleados, setEmpleados] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [departamentoFiltro, setDepartamentoFiltro] = useState('')

  useEffect(() => {
    const parametros = new URLSearchParams()
    if (busqueda) parametros.set('busqueda', busqueda)
    if (departamentoFiltro) parametros.set('departamento', departamentoFiltro)

    fetch(`/api/empleados?${parametros.toString()}`)
      .then((respuesta) => respuesta.json())
      .then(setEmpleados)
      .catch(() => setEmpleados([]))
  }, [busqueda, departamentoFiltro, recargarContador])

  return (
    <section>
      <h1>Directorio de empleados</h1>
      <div className="filtros">
        <input
          data-testid="buscar-empleados"
          placeholder="Buscar por nombre o correo"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
        <select
          data-testid="filtro-departamento"
          value={departamentoFiltro}
          onChange={(e) => setDepartamentoFiltro(e.target.value)}
        >
          <option value="">Todos los departamentos</option>
          {departamentos.map((departamento) => (
            <option key={departamento} value={departamento}>
              {departamento}
            </option>
          ))}
        </select>
      </div>

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">No se encontraron resultados</p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <tr
                key={empleado.id}
                data-testid={`fila-empleado-${empleado.id}`}
              >
                <td data-testid={`numero-empleado-${empleado.id}`}>
                  {empleado.numero_empleado}
                </td>
                <td>{empleado.nombre}</td>
                <td>{empleado.puesto}</td>
                <td>{empleado.departamento}</td>
                <td data-testid={`estado-empleado-${empleado.id}`}>
                  {empleado.estado === 'baja' ? 'Baja' : 'Activo'}
                </td>
                <td>
                  <button
                    type="button"
                    data-testid={`editar-empleado-${empleado.id}`}
                    onClick={() => onEditar(empleado)}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    data-testid={`baja-empleado-${empleado.id}`}
                    disabled={empleado.estado === 'baja'}
                    onClick={() => onBaja(empleado)}
                  >
                    Dar de baja
                  </button>
                  {empleado.estado !== 'baja' && (
                    <button
                      type="button"
                      data-testid={`vacaciones-abrir-${empleado.id}`}
                      onClick={() => onVacaciones(empleado)}
                    >
                      Solicitar vacaciones
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

export default function App() {
  const [departamentos, setDepartamentos] = useState([])
  const [datos, setDatos] = useState(DATOS_INICIALES)
  const [campoConError, setCampoConError] = useState(null)
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')
  const [recargarContador, setRecargarContador] = useState(0)
  const [empleadoEditando, setEmpleadoEditando] = useState(null)
  const [datosEdicion, setDatosEdicion] = useState({ puesto: '', departamento: '' })
  const [empleadoBaja, setEmpleadoBaja] = useState(null)
  const [fechaBaja, setFechaBaja] = useState('')
  const [empleadoVacaciones, setEmpleadoVacaciones] = useState(null)
  const [fechaInicioVac, setFechaInicioVac] = useState('')
  const [fechaFinVac, setFechaFinVac] = useState('')
  const [diasDisponiblesVac, setDiasDisponiblesVac] = useState(null)
  const [mensajeVacaciones, setMensajeVacaciones] = useState('')

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  function actualizarCampo(campo, valor) {
    setDatos((anterior) => ({ ...anterior, [campo]: valor }))
  }

  async function registrarEmpleado(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    setCampoConError(null)

    const respuesta = await fetch('/api/empleados', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos),
    })
    const cuerpo = await respuesta.json()

    if (!respuesta.ok) {
      setMensajeError(cuerpo.detail)
      setCampoConError(campoDesdeMensaje(cuerpo.detail))
      return
    }

    setMensajeExito(`Empleado ${cuerpo.numero_empleado} registrado con éxito`)
    setDatos(DATOS_INICIALES)
    setRecargarContador((anterior) => anterior + 1)
  }

  function abrirEdicion(empleado) {
    setMensajeExito('')
    setMensajeError('')
    setCampoConError(null)
    setEmpleadoBaja(null)
    setEmpleadoEditando(empleado)
    setDatosEdicion({ puesto: empleado.puesto, departamento: empleado.departamento })
  }

  function abrirBaja(empleado) {
    setMensajeExito('')
    setMensajeError('')
    setCampoConError(null)
    setEmpleadoEditando(null)
    setEmpleadoBaja(empleado)
    setFechaBaja('')
  }

  function abrirVacaciones(empleado) {
    setMensajeExito('')
    setMensajeError('')
    setCampoConError(null)
    setEmpleadoEditando(null)
    setEmpleadoBaja(null)
    setEmpleadoVacaciones(empleado)
    setFechaInicioVac('')
    setFechaFinVac('')
    setMensajeVacaciones('')
    setDiasDisponiblesVac(null)

    fetch(`/api/empleados/${empleado.id}/vacaciones`)
      .then((respuesta) => respuesta.json())
      .then((cuerpo) => setDiasDisponiblesVac(cuerpo.dias_disponibles))
      .catch(() => setDiasDisponiblesVac(null))
  }

  async function guardarEdicion(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    setCampoConError(null)

    const respuesta = await fetch(`/api/empleados/${empleadoEditando.numero_empleado}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosEdicion),
    })
    const cuerpo = await respuesta.json()

    if (!respuesta.ok) {
      setMensajeError(cuerpo.detail)
      setCampoConError(campoDesdeMensaje(cuerpo.detail))
      return
    }

    setMensajeExito(`Empleado ${cuerpo.numero_empleado} actualizado con éxito`)
    setEmpleadoEditando(null)
    setRecargarContador((anterior) => anterior + 1)
  }

  async function confirmarBaja(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    setCampoConError(null)

    const respuesta = await fetch(`/api/empleados/${empleadoBaja.numero_empleado}/baja`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fecha_baja: fechaBaja }),
    })
    const cuerpo = await respuesta.json()

    if (!respuesta.ok) {
      setMensajeError(cuerpo.detail)
      setCampoConError(campoDesdeMensaje(cuerpo.detail))
      return
    }

    setMensajeExito(`Empleado ${cuerpo.numero_empleado} dado de baja con éxito`)
    setEmpleadoBaja(null)
    setRecargarContador((anterior) => anterior + 1)
  }

  async function solicitarVacaciones(evento) {
    evento.preventDefault()
    setMensajeVacaciones('')

    const respuesta = await fetch(`/api/empleados/${empleadoVacaciones.id}/vacaciones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fecha_inicio: fechaInicioVac, fecha_fin: fechaFinVac }),
    })
    const cuerpo = await respuesta.json()

    if (!respuesta.ok) {
      setMensajeVacaciones(cuerpo.detail)
      return
    }

    const anio = fechaInicioVac.slice(0, 4)
    setMensajeVacaciones(
      `Solicitud registrada: ${cuerpo.dias_habiles} días hábiles. Te quedan ${cuerpo.dias_restantes} días hábiles en ${anio}.`
    )
    setDiasDisponiblesVac(cuerpo.dias_restantes)
  }

  return (
    <main>
      {empleadoEditando ? (
        <>
          <h1>Editar empleado {empleadoEditando.numero_empleado}</h1>
          <form onSubmit={guardarEdicion} noValidate>
            <label>
              Puesto
              <input
                data-testid="empleado-puesto"
                aria-invalid={campoConError === 'puesto'}
                value={datosEdicion.puesto}
                onChange={(e) =>
                  setDatosEdicion((anterior) => ({ ...anterior, puesto: e.target.value }))
                }
              />
            </label>

            <label>
              Departamento
              <select
                data-testid="empleado-departamento"
                aria-invalid={campoConError === 'departamento'}
                value={datosEdicion.departamento}
                onChange={(e) =>
                  setDatosEdicion((anterior) => ({ ...anterior, departamento: e.target.value }))
                }
              >
                <option value="">Selecciona un departamento</option>
                {departamentos.map((departamento) => (
                  <option key={departamento} value={departamento}>
                    {departamento}
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" data-testid="empleado-guardar">
              Guardar
            </button>
            <button type="button" onClick={() => setEmpleadoEditando(null)}>
              Cancelar
            </button>
          </form>
        </>
      ) : empleadoBaja ? (
        <>
          <h1>Dar de baja a {empleadoBaja.numero_empleado}</h1>
          <form onSubmit={confirmarBaja} noValidate>
            <label>
              Fecha de baja
              <input
                type="date"
                data-testid="empleado-fecha-baja"
                aria-invalid={campoConError === 'fecha_baja'}
                value={fechaBaja}
                onChange={(e) => setFechaBaja(e.target.value)}
              />
            </label>

            <button type="submit" data-testid="confirmar-baja">
              Confirmar baja
            </button>
            <button type="button" onClick={() => setEmpleadoBaja(null)}>
              Cancelar
            </button>
          </form>
        </>
      ) : empleadoVacaciones ? (
        <>
          <h1>Solicitar vacaciones para {empleadoVacaciones.numero_empleado}</h1>
          {diasDisponiblesVac !== null && (
            <p data-testid="vacaciones-disponibles">
              Días disponibles en el año: {diasDisponiblesVac}
            </p>
          )}
          <form onSubmit={solicitarVacaciones} noValidate>
            <label>
              Fecha de inicio
              <input
                type="date"
                data-testid="vacaciones-fecha-inicio"
                value={fechaInicioVac}
                onChange={(e) => setFechaInicioVac(e.target.value)}
              />
            </label>

            <label>
              Fecha de fin
              <input
                type="date"
                data-testid="vacaciones-fecha-fin"
                value={fechaFinVac}
                onChange={(e) => setFechaFinVac(e.target.value)}
              />
            </label>

            <button type="submit" data-testid="vacaciones-enviar">
              Solicitar
            </button>
            <button type="button" onClick={() => setEmpleadoVacaciones(null)}>
              Cancelar
            </button>
          </form>

          {mensajeVacaciones && <p data-testid="vacaciones-mensaje">{mensajeVacaciones}</p>}
        </>
      ) : (
        <>
          <h1>Registrar empleado</h1>
          <form onSubmit={registrarEmpleado} noValidate>
            <label>
              Nombre
              <input
                data-testid="empleado-nombre"
                aria-invalid={campoConError === 'nombre'}
                value={datos.nombre}
                onChange={(e) => actualizarCampo('nombre', e.target.value)}
              />
            </label>

            <label>
              Correo
              <input
                data-testid="empleado-correo"
                aria-invalid={campoConError === 'correo'}
                value={datos.correo}
                onChange={(e) => actualizarCampo('correo', e.target.value)}
              />
            </label>

            <label>
              Puesto
              <input
                data-testid="empleado-puesto"
                aria-invalid={campoConError === 'puesto'}
                value={datos.puesto}
                onChange={(e) => actualizarCampo('puesto', e.target.value)}
              />
            </label>

            <label>
              Departamento
              <select
                data-testid="empleado-departamento"
                aria-invalid={campoConError === 'departamento'}
                value={datos.departamento}
                onChange={(e) => actualizarCampo('departamento', e.target.value)}
              >
                <option value="">Selecciona un departamento</option>
                {departamentos.map((departamento) => (
                  <option key={departamento} value={departamento}>
                    {departamento}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Fecha de ingreso
              <input
                type="date"
                data-testid="empleado-fecha-ingreso"
                aria-invalid={campoConError === 'fecha_ingreso'}
                value={datos.fecha_ingreso}
                onChange={(e) => actualizarCampo('fecha_ingreso', e.target.value)}
              />
            </label>

            <button type="submit" data-testid="empleado-guardar">
              Guardar
            </button>
          </form>
        </>
      )}

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}

      <Directorio
        departamentos={departamentos}
        recargarContador={recargarContador}
        onEditar={abrirEdicion}
        onBaja={abrirBaja}
        onVacaciones={abrirVacaciones}
      />
    </main>
  )
}
