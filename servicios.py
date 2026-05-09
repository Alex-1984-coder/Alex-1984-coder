"""
servicios.py - Clase abstracta Servicio y servicios especializados - Software FJ

Servicios disponibles:
  1. ReservaSala       - Alquiler de salas de reuniones
  2. AlquilerEquipo    - Alquiler de equipos tecnológicos
  3. AsesoriaEspecializada - Consultoría y asesoría profesional

Principios OOP: Abstracción, Herencia, Polimorfismo, Encapsulación
"""

from abc import abstractmethod
from entidades import EntidadBase
from excepciones import (
    ParametroServicioInvalidoError,
    ServicioNoDisponibleError,
    CostoInconsistenteError,
    ServicioNoEncontradoError,
)
import logger


# ══════════════════════════════════════════════════════
# CLASE ABSTRACTA SERVICIO
# ══════════════════════════════════════════════════════
class Servicio(EntidadBase):
    """
    Clase abstracta base para todos los servicios de Software FJ.
    Define la interfaz común que deben implementar los servicios especializados.
    """

    IMPUESTO_BASE = 0.19  # IVA 19 % Colombia

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_hora: float,
        disponible: bool = True,
    ):
        if tarifa_hora <= 0:
            raise ParametroServicioInvalidoError("tarifa_hora", "debe ser mayor a 0")
        super().__init__(id_servicio, nombre)
        self._tarifa_hora = tarifa_hora
        self._disponible = disponible

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, estado: bool):
        self._disponible = estado
        logger.info(f"Servicio '{self._nombre}' disponibilidad → {estado}")

    # ── Métodos abstractos que cada servicio DEBE implementar ──
    @abstractmethod
    def calcular_costo(self, horas: float, **kwargs) -> float:
        """Calcula el costo base del servicio."""
        ...

    @abstractmethod
    def validar_parametros(self, horas: float, **kwargs) -> bool:
        """Valida que los parámetros sean correctos para este servicio."""
        ...

    @abstractmethod
    def descripcion_detallada(self) -> str:
        """Descripción extendida con características del servicio."""
        ...

    # ── Métodos concretos (herencia) ──────────────────
    def describir(self) -> str:
        estado = "✅ Disponible" if self._disponible else "❌ No disponible"
        return (
            f"[{self.__class__.__name__}] {self._nombre} | "
            f"ID: {self._id} | Tarifa: ${self._tarifa_hora:,.0f}/h | {estado}"
        )

    def validar(self) -> bool:
        return self._tarifa_hora > 0 and bool(self._nombre)

    # ── Métodos sobrecargados (simulados con parámetros opcionales) ──
    def calcular_costo_con_impuesto(
        self,
        horas: float,
        incluir_iva: bool = True,
        descuento: float = 0.0,
        **kwargs,
    ) -> dict:
        """
        Versión sobrecargada del cálculo de costo.
        Permite incluir IVA y aplicar descuento porcentual.
        Retorna desglose completo.
        """
        try:
            if not self._disponible:
                raise ServicioNoDisponibleError(self._nombre)

            self.validar_parametros(horas, **kwargs)

            if not (0.0 <= descuento < 1.0):
                raise ParametroServicioInvalidoError(
                    "descuento", f"debe estar entre 0.0 y 0.99, recibido {descuento}"
                )

            base = self.calcular_costo(horas, **kwargs)

            if base < 0:
                raise CostoInconsistenteError(f"el costo base es negativo: {base}")

            valor_descuento = base * descuento
            subtotal = base - valor_descuento
            iva = subtotal * self.IMPUESTO_BASE if incluir_iva else 0.0
            total = subtotal + iva

            return {
                "base": round(base, 2),
                "descuento_aplicado": round(valor_descuento, 2),
                "subtotal": round(subtotal, 2),
                "iva": round(iva, 2),
                "total": round(total, 2),
                "incluye_iva": incluir_iva,
                "horas": horas,
            }

        except (ServicioNoDisponibleError, ParametroServicioInvalidoError,
                CostoInconsistenteError):
            raise
        except Exception as e:
            raise CostoInconsistenteError(str(e)) from e

    def calcular_costo_simple(self, horas: float) -> float:
        """Sobrecarga simplificada: solo costo base sin extras."""
        self.validar_parametros(horas)
        return self.calcular_costo(horas)

    def calcular_costo_corporativo(
        self, horas: float, num_personas: int, descuento_vol: float = 0.10
    ) -> dict:
        """Sobrecarga corporativa: aplica descuento por volumen de personas."""
        if num_personas < 1:
            raise ParametroServicioInvalidoError("num_personas", "debe ser ≥ 1")
        descuento_total = min(descuento_vol * (num_personas // 5), 0.40)
        return self.calcular_costo_con_impuesto(horas, descuento=descuento_total)


# ══════════════════════════════════════════════════════
# SERVICIO 1: RESERVA DE SALA
# ══════════════════════════════════════════════════════
class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones.
    Incluye capacidad máxima y equipamiento disponible.
    """

    DURACION_MIN = 1.0   # horas
    DURACION_MAX = 8.0

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_hora: float,
        capacidad_max: int,
        tiene_proyector: bool = False,
        tiene_videoconferencia: bool = False,
    ):
        if capacidad_max < 1:
            raise ParametroServicioInvalidoError("capacidad_max", "debe ser ≥ 1")
        super().__init__(id_servicio, nombre, tarifa_hora)
        self._capacidad_max = capacidad_max
        self._tiene_proyector = tiene_proyector
        self._tiene_videoconferencia = tiene_videoconferencia

    @property
    def capacidad_max(self) -> int:
        return self._capacidad_max

    def calcular_costo(self, horas: float, num_asistentes: int = 1, **kwargs) -> float:
        """Costo base: tarifa × horas. Recargo del 10 % si > 50 % capacidad."""
        base = self._tarifa_hora * horas
        if num_asistentes > self._capacidad_max * 0.5:
            base *= 1.10  # recargo por alta ocupación
        return base

    def validar_parametros(self, horas: float, num_asistentes: int = 1, **kwargs) -> bool:
        if not (self.DURACION_MIN <= horas <= self.DURACION_MAX):
            raise ParametroServicioInvalidoError(
                "horas",
                f"para sala debe estar entre {self.DURACION_MIN}h y {self.DURACION_MAX}h"
            )
        if num_asistentes < 1:
            raise ParametroServicioInvalidoError("num_asistentes", "debe ser ≥ 1")
        if num_asistentes > self._capacidad_max:
            raise ParametroServicioInvalidoError(
                "num_asistentes",
                f"excede la capacidad máxima de {self._capacidad_max} personas"
            )
        return True

    def descripcion_detallada(self) -> str:
        extras = []
        if self._tiene_proyector:
            extras.append("Proyector")
        if self._tiene_videoconferencia:
            extras.append("Videoconferencia")
        extras_str = ", ".join(extras) if extras else "Sin extras"
        return (
            f"SALA DE REUNIONES: {self._nombre}\n"
            f"  Capacidad máx.: {self._capacidad_max} personas\n"
            f"  Equipamiento:   {extras_str}\n"
            f"  Tarifa:         ${self._tarifa_hora:,.0f}/hora\n"
            f"  Duración:       {self.DURACION_MIN}h – {self.DURACION_MAX}h"
        )


# ══════════════════════════════════════════════════════
# SERVICIO 2: ALQUILER DE EQUIPO
# ══════════════════════════════════════════════════════
class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    Aplica recargo por tiempo extendido y depósito de garantía.
    """

    DURACION_MIN = 2.0
    DURACION_MAX = 72.0
    HORAS_RECARGO = 8.0      # a partir de aquí se aplica recargo
    PORCENTAJE_RECARGO = 0.15
    DEPOSITO_BASE = 50_000   # COP

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_hora: float,
        tipo_equipo: str,
        requiere_deposito: bool = True,
    ):
        tipos_validos = ("laptop", "camara", "drone", "proyector", "servidor", "otro")
        if tipo_equipo not in tipos_validos:
            raise ParametroServicioInvalidoError(
                "tipo_equipo", f"debe ser uno de: {tipos_validos}"
            )
        super().__init__(id_servicio, nombre, tarifa_hora)
        self._tipo_equipo = tipo_equipo
        self._requiere_deposito = requiere_deposito

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """Costo base con recargo por uso extendido."""
        if horas <= self.HORAS_RECARGO:
            return self._tarifa_hora * horas
        costo_normal = self._tarifa_hora * self.HORAS_RECARGO
        horas_extra = horas - self.HORAS_RECARGO
        costo_extra = self._tarifa_hora * horas_extra * (1 + self.PORCENTAJE_RECARGO)
        return costo_normal + costo_extra

    def calcular_deposito(self) -> float:
        return self.DEPOSITO_BASE if self._requiere_deposito else 0.0

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        if not (self.DURACION_MIN <= horas <= self.DURACION_MAX):
            raise ParametroServicioInvalidoError(
                "horas",
                f"para equipo debe estar entre {self.DURACION_MIN}h y {self.DURACION_MAX}h"
            )
        return True

    def descripcion_detallada(self) -> str:
        deposito_info = f"${self.DEPOSITO_BASE:,.0f}" if self._requiere_deposito else "No requerido"
        return (
            f"ALQUILER DE EQUIPO: {self._nombre}\n"
            f"  Tipo:           {self._tipo_equipo.upper()}\n"
            f"  Tarifa base:    ${self._tarifa_hora:,.0f}/hora\n"
            f"  Recargo +{self.HORAS_RECARGO}h: {int(self.PORCENTAJE_RECARGO*100)}%\n"
            f"  Depósito:       {deposito_info}\n"
            f"  Duración:       {self.DURACION_MIN}h – {self.DURACION_MAX}h"
        )


# ══════════════════════════════════════════════════════
# SERVICIO 3: ASESORÍA ESPECIALIZADA
# ══════════════════════════════════════════════════════
class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría y consultoría profesional.
    El costo varía según el nivel del asesor y el área temática.
    """

    DURACION_MIN = 0.5   # media hora mínima
    DURACION_MAX = 4.0

    MULTIPLICADORES_NIVEL = {
        "junior": 1.0,
        "senior": 1.5,
        "experto": 2.0,
    }

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_hora: float,
        area: str,
        nivel_asesor: str = "senior",
    ):
        if nivel_asesor not in self.MULTIPLICADORES_NIVEL:
            raise ParametroServicioInvalidoError(
                "nivel_asesor",
                f"debe ser uno de: {list(self.MULTIPLICADORES_NIVEL.keys())}"
            )
        super().__init__(id_servicio, nombre, tarifa_hora)
        self._area = area
        self._nivel_asesor = nivel_asesor

    @property
    def area(self) -> str:
        return self._area

    @property
    def nivel_asesor(self) -> str:
        return self._nivel_asesor

    def calcular_costo(self, horas: float, **kwargs) -> float:
        """Costo según tarifa base × multiplicador de nivel."""
        multiplicador = self.MULTIPLICADORES_NIVEL[self._nivel_asesor]
        return self._tarifa_hora * horas * multiplicador

    def validar_parametros(self, horas: float, **kwargs) -> bool:
        if not (self.DURACION_MIN <= horas <= self.DURACION_MAX):
            raise ParametroServicioInvalidoError(
                "horas",
                f"para asesoría debe estar entre {self.DURACION_MIN}h y {self.DURACION_MAX}h"
            )
        return True

    def descripcion_detallada(self) -> str:
        mult = self.MULTIPLICADORES_NIVEL[self._nivel_asesor]
        tarifa_real = self._tarifa_hora * mult
        return (
            f"ASESORÍA ESPECIALIZADA: {self._nombre}\n"
            f"  Área:           {self._area}\n"
            f"  Nivel asesor:   {self._nivel_asesor.upper()} (×{mult})\n"
            f"  Tarifa efectiva:${tarifa_real:,.0f}/hora\n"
            f"  Duración:       {self.DURACION_MIN}h – {self.DURACION_MAX}h"
        )


# ══════════════════════════════════════════════════════
# REPOSITORIO DE SERVICIOS
# ══════════════════════════════════════════════════════
class RepositorioServicios:
    """Gestiona el catálogo de servicios disponibles en memoria."""

    def __init__(self):
        self._servicios: dict[str, Servicio] = {}

    def agregar(self, servicio: Servicio) -> Servicio:
        try:
            if not servicio.validar():
                raise ParametroServicioInvalidoError("servicio", "datos inválidos")
            self._servicios[servicio.id] = servicio
            logger.evento(f"Servicio agregado: {servicio.id} - {servicio.nombre}")
            return servicio
        except ParametroServicioInvalidoError:
            logger.error(f"Error al agregar servicio {servicio.id}")
            raise

    def buscar(self, id_servicio: str) -> Servicio:
        svc = self._servicios.get(id_servicio)
        if not svc:
            raise ServicioNoEncontradoError(id_servicio)
        return svc

    def listar_disponibles(self) -> list:
        return [s for s in self._servicios.values() if s.disponible]

    def listar_todos(self) -> list:
        return list(self._servicios.values())

    def total(self) -> int:
        return len(self._servicios)
