"""
reservas.py - Clase Reserva e integración con Cliente y Servicio - Software FJ

Estados de una reserva:
  PENDIENTE → CONFIRMADA → PROCESADA
                         → CANCELADA
  PENDIENTE → CANCELADA

Principios OOP: Encapsulación, manejo de excepciones, integración de objetos.
"""

import uuid
from datetime import datetime
from entidades import Cliente
from servicios import Servicio
from excepciones import (
    ReservaOperacionInvalidaError,
    DuracionInvalidaError,
    ReservaNoEncontradaError,
    ReservaConflictoError,
    ServicioNoDisponibleError,
    ParametroServicioInvalidoError,
)
import logger


# ══════════════════════════════════════════════════════
# CLASE RESERVA
# ══════════════════════════════════════════════════════
class Reserva:
    """
    Representa una reserva que integra un Cliente, un Servicio,
    una duración y un estado. Implementa el ciclo de vida completo
    con manejo de excepciones en cada transición.
    """

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "PROCESADA", "CANCELADA")

    # Transiciones permitidas: estado_actual → estados_destino
    TRANSICIONES = {
        "PENDIENTE":   {"CONFIRMADA", "CANCELADA"},
        "CONFIRMADA":  {"PROCESADA", "CANCELADA"},
        "PROCESADA":   set(),
        "CANCELADA":   set(),
    }

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        notas: str = "",
        **parametros_servicio,
    ):
        # ── Validación del servicio ──
        if not servicio.disponible:
            raise ServicioNoDisponibleError(servicio.nombre)

        # ── Validación de parámetros del servicio ──
        try:
            servicio.validar_parametros(horas, **parametros_servicio)
        except ParametroServicioInvalidoError as e:
            raise DuracionInvalidaError(horas, 0, 99) from e

        self._id = str(uuid.uuid4())[:8].upper()
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._parametros = parametros_servicio
        self._notas = notas
        self._estado = "PENDIENTE"
        self._fecha_creacion = datetime.now()
        self._fecha_actualizacion = datetime.now()
        self._costo_calculado: dict = {}
        self._historial: list[str] = [
            f"{self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')} — Reserva creada (PENDIENTE)"
        ]

        # Registrar en el cliente
        cliente.agregar_reserva(self._id)
        logger.evento(
            f"Reserva {self._id} creada | Cliente: {cliente.id} | "
            f"Servicio: {servicio.id} | Horas: {horas}"
        )

    # ── Propiedades ───────────────────────────────────
    @property
    def id(self) -> str:
        return self._id

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo(self) -> dict:
        return self._costo_calculado

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    # ── Transiciones de estado ────────────────────────
    def _cambiar_estado(self, nuevo_estado: str, motivo: str = ""):
        if nuevo_estado not in self.TRANSICIONES[self._estado]:
            raise ReservaOperacionInvalidaError(nuevo_estado, self._estado)
        estado_anterior = self._estado
        self._estado = nuevo_estado
        self._fecha_actualizacion = datetime.now()
        entrada = (
            f"{self._fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S')} — "
            f"{estado_anterior} → {nuevo_estado}"
            + (f" ({motivo})" if motivo else "")
        )
        self._historial.append(entrada)
        logger.evento(
            f"Reserva {self._id}: {estado_anterior} → {nuevo_estado}"
            + (f" | {motivo}" if motivo else "")
        )

    def confirmar(self, incluir_iva: bool = True, descuento: float = 0.0) -> dict:
        """
        Confirma la reserva y calcula el costo definitivo.
        Usa try/except/else/finally para garantizar estabilidad.
        """
        try:
            self._cambiar_estado("CONFIRMADA", "confirmación manual")
            costo = self._servicio.calcular_costo_con_impuesto(
                self._horas,
                incluir_iva=incluir_iva,
                descuento=descuento,
                **self._parametros,
            )
        except ReservaOperacionInvalidaError as e:
            logger.error(f"No se pudo confirmar reserva {self._id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al confirmar reserva {self._id}: {e}")
            raise ReservaConflictoError(str(e)) from e
        else:
            self._costo_calculado = costo
            logger.info(
                f"Reserva {self._id} confirmada | Total: ${costo['total']:,.2f}"
            )
            return costo
        finally:
            logger.info(f"Proceso de confirmación de reserva {self._id} finalizado")

    def procesar(self) -> bool:
        """
        Procesa la reserva (marca como ejecutada).
        Usa try/except/finally.
        """
        try:
            if not self._costo_calculado:
                raise ReservaConflictoError(
                    "se intentó procesar sin haber calculado el costo (confirmar primero)"
                )
            self._cambiar_estado("PROCESADA", "servicio entregado")
            return True
        except (ReservaOperacionInvalidaError, ReservaConflictoError) as e:
            logger.error(f"Error al procesar reserva {self._id}: {e}")
            raise
        finally:
            logger.info(f"Intento de procesamiento de reserva {self._id} completado")

    def cancelar(self, motivo: str = "sin motivo especificado") -> bool:
        """
        Cancela la reserva y libera al cliente.
        Usa try/except/else.
        """
        try:
            self._cambiar_estado("CANCELADA", motivo)
        except ReservaOperacionInvalidaError as e:
            logger.error(f"No se pudo cancelar reserva {self._id}: {e}")
            raise
        else:
            self._cliente.eliminar_reserva(self._id)
            logger.evento(f"Reserva {self._id} cancelada: {motivo}")
            return True

    # ── Representación ────────────────────────────────
    def describir(self) -> str:
        costo_str = (
            f"${self._costo_calculado.get('total', 0):,.2f}"
            if self._costo_calculado
            else "Por calcular"
        )
        return (
            f"RESERVA {self._id}\n"
            f"  Cliente:  {self._cliente.nombre} ({self._cliente.id})\n"
            f"  Servicio: {self._servicio.nombre}\n"
            f"  Horas:    {self._horas}h\n"
            f"  Estado:   {self._estado}\n"
            f"  Costo:    {costo_str}\n"
            f"  Creada:   {self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def historial_estados(self) -> str:
        return "\n".join(f"  • {h}" for h in self._historial)

    def __str__(self) -> str:
        return self.describir()


# ══════════════════════════════════════════════════════
# REPOSITORIO DE RESERVAS
# ══════════════════════════════════════════════════════
class RepositorioReservas:
    """Gestiona todas las reservas del sistema en memoria."""

    def __init__(self):
        self._reservas: dict[str, Reserva] = {}

    def crear(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        notas: str = "",
        **params,
    ) -> Reserva:
        try:
            reserva = Reserva(cliente, servicio, horas, notas, **params)
            self._reservas[reserva.id] = reserva
            return reserva
        except Exception as e:
            logger.error(f"Error al crear reserva: {e}", e)
            raise

    def buscar(self, id_reserva: str) -> Reserva:
        r = self._reservas.get(id_reserva)
        if not r:
            raise ReservaNoEncontradaError(id_reserva)
        return r

    def listar_por_cliente(self, id_cliente: str) -> list:
        return [
            r for r in self._reservas.values()
            if r.cliente.id == id_cliente
        ]

    def listar_por_estado(self, estado: str) -> list:
        return [
            r for r in self._reservas.values()
            if r.estado == estado
        ]

    def listar_todas(self) -> list:
        return list(self._reservas.values())

    def total(self) -> int:
        return len(self._reservas)
