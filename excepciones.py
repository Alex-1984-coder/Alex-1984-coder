"""
excepciones.py - Excepciones personalizadas del sistema Software FJ
Equipo de desarrollo: Software FJ
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


# ──────────────────────────────────────────────
# Excepciones de Cliente
# ──────────────────────────────────────────────
class ClienteError(SoftwareFJError):
    """Excepción base para errores relacionados con clientes."""
    def __init__(self, mensaje: str, codigo: str = "ERR_CLIENTE"):
        super().__init__(mensaje, codigo)


class ClienteYaExisteError(ClienteError):
    def __init__(self, identificacion: str):
        super().__init__(
            f"El cliente con identificación '{identificacion}' ya está registrado.",
            "ERR_CLIENTE_DUPLICADO"
        )


class ClienteNoEncontradoError(ClienteError):
    def __init__(self, identificacion: str):
        super().__init__(
            f"No se encontró ningún cliente con identificación '{identificacion}'.",
            "ERR_CLIENTE_NO_ENCONTRADO"
        )


class DatosClienteInvalidosError(ClienteError):
    def __init__(self, campo: str, valor):
        super().__init__(
            f"El campo '{campo}' tiene un valor inválido: '{valor}'.",
            "ERR_CLIENTE_DATOS_INVALIDOS"
        )


# ──────────────────────────────────────────────
# Excepciones de Servicio
# ──────────────────────────────────────────────
class ServicioError(SoftwareFJError):
    """Excepción base para errores relacionados con servicios."""
    def __init__(self, mensaje: str, codigo: str = "ERR_SERVICIO"):
        super().__init__(mensaje, codigo)


class ServicioNoDisponibleError(ServicioError):
    def __init__(self, nombre_servicio: str):
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible actualmente.",
            "ERR_SERVICIO_NO_DISPONIBLE"
        )


class ServicioNoEncontradoError(ServicioError):
    def __init__(self, id_servicio: str):
        super().__init__(
            f"No se encontró el servicio con ID '{id_servicio}'.",
            "ERR_SERVICIO_NO_ENCONTRADO"
        )


class ParametroServicioInvalidoError(ServicioError):
    def __init__(self, parametro: str, razon: str):
        super().__init__(
            f"Parámetro inválido '{parametro}': {razon}.",
            "ERR_SERVICIO_PARAMETRO"
        )


class CostoInconsistenteError(ServicioError):
    def __init__(self, detalle: str):
        super().__init__(
            f"Cálculo de costo inconsistente: {detalle}.",
            "ERR_SERVICIO_COSTO"
        )


# ──────────────────────────────────────────────
# Excepciones de Reserva
# ──────────────────────────────────────────────
class ReservaError(SoftwareFJError):
    """Excepción base para errores relacionados con reservas."""
    def __init__(self, mensaje: str, codigo: str = "ERR_RESERVA"):
        super().__init__(mensaje, codigo)


class ReservaNoEncontradaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(
            f"No se encontró la reserva con ID '{id_reserva}'.",
            "ERR_RESERVA_NO_ENCONTRADA"
        )


class ReservaOperacionInvalidaError(ReservaError):
    def __init__(self, operacion: str, estado_actual: str):
        super().__init__(
            f"Operación '{operacion}' no permitida en estado '{estado_actual}'.",
            "ERR_RESERVA_OPERACION"
        )


class DuracionInvalidaError(ReservaError):
    def __init__(self, duracion, minimo: float, maximo: float):
        super().__init__(
            f"Duración '{duracion}h' fuera del rango permitido [{minimo}h – {maximo}h].",
            "ERR_RESERVA_DURACION"
        )


class ReservaConflictoError(ReservaError):
    def __init__(self, detalle: str):
        super().__init__(
            f"Conflicto en la reserva: {detalle}.",
            "ERR_RESERVA_CONFLICTO"
        )
