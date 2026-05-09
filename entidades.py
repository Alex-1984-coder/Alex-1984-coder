"""
entidades.py - Clase abstracta base y clase Cliente - Software FJ
"""

# Módulo para trabajar con expresiones regulares (validación de correo, teléfono, etc.)
import re
# ABC: clase base para crear clases abstractas; abstractmethod: decorador para métodos obligatorios
from abc import ABC, abstractmethod
# Se importan las excepciones personalizadas que se lanzarán cuando los datos sean inválidos
from excepciones import (
    DatosClienteInvalidosError,   # Cuando un campo del cliente tiene valor incorrecto
    ClienteYaExisteError,         # Cuando se intenta registrar un cliente duplicado
    ClienteNoEncontradoError,     # Cuando se busca un cliente que no existe
)
# Módulo propio de registro de eventos y errores en el archivo de logs
import logger


# ══════════════════════════════════════════════════════
# CLASE ABSTRACTA BASE
# ══════════════════════════════════════════════════════
class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad registrable en el sistema.
    Principios aplicados: Abstracción, Encapsulación.
    """

    def __init__(self, id_entidad: str, nombre: str):
        # Atributo protegido: identificador único de la entidad (accesible en subclases)
        self._id = id_entidad
        # Atributo protegido: nombre legible de la entidad
        self._nombre = nombre
        # Toda entidad comienza como activa al momento de su creación
        self._activo = True

    @property
    def id(self) -> str:
        # Propiedad de solo lectura que expone el ID sin permitir modificación externa
        return self._id

    @property
    def nombre(self) -> str:
        # Propiedad de solo lectura que expone el nombre sin permitir modificación externa
        return self._nombre

    @property
    def activo(self) -> bool:
        # Propiedad de solo lectura que indica si la entidad está habilitada en el sistema
        return self._activo

    def desactivar(self):
        # Cambia el estado de la entidad a inactivo (baja lógica, no se elimina del sistema)
        self._activo = False

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción textual de la entidad."""
        # Método abstracto: cada subclase DEBE implementar su propia versión de describir()
        ...

    @abstractmethod
    def validar(self) -> bool:
        """Valida que los datos de la entidad sean correctos."""
        # Método abstracto: cada subclase DEBE definir sus propias reglas de validación
        ...

    def __str__(self) -> str:
        # Cuando se imprime el objeto con print(), llama automáticamente a describir()
        return self.describir()

    def __repr__(self) -> str:
        # Representación técnica del objeto, útil para depuración en consola o logs
        return f"{self.__class__.__name__}(id='{self._id}', nombre='{self._nombre}')"


# ══════════════════════════════════════════════════════
# CLASE CLIENTE
# ══════════════════════════════════════════════════════
class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.
    Aplica encapsulación estricta y validación de datos personales.
    """

    def __init__(
        self,
        identificacion: str,   # Cédula, NIT u otro documento único del cliente
        nombre: str,           # Nombre completo o razón social
        correo: str,           # Correo electrónico de contacto
        telefono: str,         # Número telefónico con o sin indicativo internacional
        tipo: str = "natural", # Tipo de cliente: persona "natural" o "empresa"
    ):
        # Se validan todos los campos ANTES de inicializar el objeto padre
        # para evitar crear un objeto en estado inválido
        self._validar_identificacion(identificacion)
        self._validar_nombre(nombre)
        self._validar_correo(correo)
        self._validar_telefono(telefono)
        self._validar_tipo(tipo)

        # Una vez validados los datos, se inicializa la clase padre con ID y nombre
        super().__init__(identificacion, nombre)
        # Doble guion bajo aplica name-mangling: el atributo se almacena como
        # _Cliente__correo, impidiendo acceso directo desde fuera de la clase
        self.__correo = correo
        # Mismo mecanismo de privacidad estricta para el teléfono
        self.__telefono = telefono
        # Tipo de cliente: se almacena como protegido (accesible en subclases)
        self._tipo = tipo
        # Lista interna que almacena los IDs de las reservas asociadas a este cliente
        self._reservas: list = []

    # ── Propiedades de acceso ──────────────────────────
    @property
    def correo(self) -> str:
        # Permite leer el correo desde fuera de la clase de forma controlada
        return self.__correo

    @correo.setter
    def correo(self, valor: str):
        # Valida el nuevo correo antes de permitir su modificación
        self._validar_correo(valor)
        # Solo asigna el nuevo valor si pasó la validación
        self.__correo = valor

    @property
    def telefono(self) -> str:
        # Permite leer el teléfono desde fuera de la clase de forma controlada
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        # Valida el nuevo teléfono antes de permitir su modificación
        self._validar_telefono(valor)
        # Solo asigna si el valor es válido
        self.__telefono = valor

    @property
    def tipo(self) -> str:
        # Expone el tipo de cliente como solo lectura (no debe cambiar después del registro)
        return self._tipo

    @property
    def num_reservas(self) -> int:
        # Calcula en tiempo real cuántas reservas tiene el cliente contando la lista interna
        return len(self._reservas)

    # ── Métodos de validación internos ────────────────
    @staticmethod
    def _validar_identificacion(valor: str):
        # Verifica que el valor exista, sea texto y no esté vacío
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise DatosClienteInvalidosError("identificacion", valor)
        # Aplica expresión regular: solo letras, números y guiones, entre 3 y 20 caracteres
        if not re.match(r"^[A-Za-z0-9\-]{3,20}$", valor.strip()):
            raise DatosClienteInvalidosError(
                "identificacion",
                f"'{valor}' — debe tener 3-20 caracteres alfanuméricos o guiones"
            )

    @staticmethod
    def _validar_nombre(valor: str):
        # El nombre debe ser texto no vacío con al menos 2 caracteres significativos
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 2:
            raise DatosClienteInvalidosError("nombre", valor)

    @staticmethod
    def _validar_correo(valor: str):
        # Patrón de expresión regular para validar formato básico de correo electrónico
        patron = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
        # Si el valor está vacío o no coincide con el patrón, se lanza la excepción
        if not valor or not re.match(patron, valor.strip()):
            raise DatosClienteInvalidosError("correo", valor)

    @staticmethod
    def _validar_telefono(valor: str):
        # Acepta números con o sin "+" al inicio, entre 7 y 15 dígitos (estándar E.164)
        if not valor or not re.match(r"^\+?[0-9]{7,15}$", valor.strip()):
            raise DatosClienteInvalidosError("telefono", valor)

    @staticmethod
    def _validar_tipo(valor: str):
        # Solo se aceptan exactamente los dos tipos definidos en el sistema
        if valor not in ("natural", "empresa"):
            raise DatosClienteInvalidosError("tipo", valor)

    # ── Métodos abstractos implementados ──────────────
    def describir(self) -> str:
        # Determina el texto del estado según el atributo heredado de EntidadBase
        estado = "Activo" if self._activo else "Inactivo"
        # Construye y retorna una cadena con todos los datos visibles del cliente
        return (
            f"Cliente [{self._tipo.upper()}] | ID: {self._id} | "
            f"Nombre: {self._nombre} | Correo: {self.__correo} | "
            f"Tel: {self.__telefono} | Reservas: {self.num_reservas} | {estado}"
        )

    def validar(self) -> bool:
        try:
            # Vuelve a ejecutar todas las validaciones sobre los datos actuales del objeto
            self._validar_identificacion(self._id)
            self._validar_nombre(self._nombre)
            self._validar_correo(self.__correo)
            self._validar_telefono(self.__telefono)
            # Si ninguna validación lanza excepción, el objeto es consistente
            return True
        except DatosClienteInvalidosError:
            # Si alguna validación falla, retorna False sin propagar la excepción
            return False

    # ── Gestión de reservas del cliente ───────────────
    def agregar_reserva(self, id_reserva: str):
        # Solo agrega el ID si no está ya en la lista (evita duplicados)
        if id_reserva not in self._reservas:
            self._reservas.append(id_reserva)

    def eliminar_reserva(self, id_reserva: str):
        # Solo elimina si el ID existe en la lista (evita errores por elemento inexistente)
        if id_reserva in self._reservas:
            self._reservas.remove(id_reserva)

    def obtener_reservas(self) -> list:
        # Retorna una COPIA de la lista para proteger la lista interna de modificaciones externas
        return list(self._reservas)


# ══════════════════════════════════════════════════════
# REPOSITORIO DE CLIENTES
# ══════════════════════════════════════════════════════
class RepositorioClientes:
    """
    Gestiona el almacenamiento en memoria de todos los clientes.
    Aplica el patrón Repository para desacoplar la lógica de acceso.
    """

    def __init__(self):
        # Diccionario que actúa como base de datos en memoria: clave=ID, valor=objeto Cliente
        self._clientes: dict[str, Cliente] = {}

    def registrar(self, cliente: Cliente) -> Cliente:
        try:
            # Verifica si ya existe un cliente con el mismo ID antes de registrar
            if cliente.id in self._clientes:
                raise ClienteYaExisteError(cliente.id)
            # Segunda verificación: confirma que el objeto mismo sea internamente válido
            if not cliente.validar():
                raise DatosClienteInvalidosError("general", "datos inconsistentes")
            # Si pasó todas las validaciones, almacena el cliente en el diccionario
            self._clientes[cliente.id] = cliente
            # Registra el evento exitoso en el archivo de logs
            logger.evento(f"Cliente registrado: {cliente.id} - {cliente.nombre}")
            # Retorna el cliente recién registrado para uso del llamador
            return cliente
        except ClienteYaExisteError:
            # Registra el intento de duplicado en logs y relanza la excepción hacia arriba
            logger.error(f"Intento de registro duplicado: {cliente.id}")
            raise
        except DatosClienteInvalidosError as e:
            # Registra el error de datos en logs y relanza para que el llamador lo maneje
            logger.error(f"Datos inválidos al registrar cliente: {e}")
            raise

    def buscar(self, identificacion: str) -> Cliente:
        # Busca el cliente en el diccionario por su ID
        cliente = self._clientes.get(identificacion)
        # Si no existe (get retorna None), lanza excepción específica
        if not cliente:
            raise ClienteNoEncontradoError(identificacion)
        # Si existe, retorna el objeto Cliente encontrado
        return cliente

    def listar_todos(self) -> list:
        # Retorna una lista con todos los objetos Cliente registrados en el sistema
        return list(self._clientes.values())

    def total(self) -> int:
        # Retorna el número total de clientes almacenados contando las claves del diccionario
        return len(self._clientes)