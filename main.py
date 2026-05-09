"""
main.py - Sistema principal Software FJ
Simula más de 10 operaciones completas (válidas e inválidas)
demostrando robustez ante errores y manejo avanzado de excepciones.

Equipo: Software FJ (5 integrantes)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from entidades import Cliente, RepositorioClientes
from servicios import (
    ReservaSala,
    AlquilerEquipo,
    AsesoriaEspecializada,
    RepositorioServicios,
)
from reservas import Reserva, RepositorioReservas
from excepciones import SoftwareFJError
import logger


# ══════════════════════════════════════════════════════
# UTILIDADES DE PRESENTACIÓN
# ══════════════════════════════════════════════════════
SEP_MAYOR = "═" * 65
SEP_MENOR = "─" * 65

def titulo(texto: str):
    print(f"\n{SEP_MAYOR}")
    print(f"  {texto}")
    print(SEP_MAYOR)

def subtitulo(texto: str):
    print(f"\n{SEP_MENOR}")
    print(f"  {texto}")
    print(SEP_MENOR)

def ok(texto: str):
    print(f"  ✅ {texto}")

def fallo(texto: str):
    print(f"  ❌ {texto}")

def info(texto: str):
    print(f"  ℹ️  {texto}")

def mostrar_costo(desglose: dict):
    print(f"     Base:      ${desglose['base']:>12,.2f}")
    if desglose['descuento_aplicado']:
        print(f"     Descuento: ${desglose['descuento_aplicado']:>12,.2f}")
    print(f"     Subtotal:  ${desglose['subtotal']:>12,.2f}")
    if desglose['incluye_iva']:
        print(f"     IVA (19%): ${desglose['iva']:>12,.2f}")
    print(f"     TOTAL:     ${desglose['total']:>12,.2f}")


# ══════════════════════════════════════════════════════
# INICIALIZACIÓN DEL SISTEMA
# ══════════════════════════════════════════════════════
def inicializar_sistema():
    """Crea e inicializa los repositorios centrales."""
    logger.evento("=== INICIO DEL SISTEMA SOFTWARE FJ ===")
    return (
        RepositorioClientes(),
        RepositorioServicios(),
        RepositorioReservas(),
    )


# ══════════════════════════════════════════════════════
# BLOQUE 1: REGISTRO DE CLIENTES
# ══════════════════════════════════════════════════════
def bloque_clientes(repo_clientes: RepositorioClientes):
    titulo("BLOQUE 1 — REGISTRO DE CLIENTES")

    # ── Operación 1: Cliente válido persona natural ──
    subtitulo("Operación 1 — Cliente válido (persona natural)")
    try:
        c1 = Cliente("CC-1001", "Ana Martínez", "ana@correo.com", "3001234567", "natural")
        repo_clientes.registrar(c1)
        ok(f"Cliente registrado: {c1.nombre}")
        logger.info(f"OP1 exitosa: {c1.describir()}")
    except SoftwareFJError as e:
        fallo(f"Error inesperado: {e}")
        logger.error("OP1 fallida", e)

    # ── Operación 2: Cliente válido empresa ──
    subtitulo("Operación 2 — Cliente válido (empresa)")
    try:
        c2 = Cliente("NIT-9002", "TechCorp SAS", "contacto@techcorp.co", "6013456789", "empresa")
        repo_clientes.registrar(c2)
        ok(f"Empresa registrada: {c2.nombre}")
        logger.info(f"OP2 exitosa: {c2.describir()}")
    except SoftwareFJError as e:
        fallo(f"Error: {e}")
        logger.error("OP2 fallida", e)

    # ── Operación 3: Correo inválido (error esperado) ──
    subtitulo("Operación 3 — Registro con correo inválido (debe fallar)")
    try:
        c_malo = Cliente("CC-1002", "Pedro Rojas", "correo-sin-arroba", "3009876543")
        repo_clientes.registrar(c_malo)
        fallo("No se detectó el error de correo")
    except SoftwareFJError as e:
        ok(f"Error capturado correctamente → {e}")
        logger.advertencia(f"OP3: correo inválido rechazado: {e}")

    # ── Operación 4: Cliente duplicado (error esperado) ──
    subtitulo("Operación 4 — Registro duplicado (debe fallar)")
    try:
        c_dup = Cliente("CC-1001", "Copia Ana", "copia@correo.com", "3001111111")
        repo_clientes.registrar(c_dup)
        fallo("No se detectó el duplicado")
    except SoftwareFJError as e:
        ok(f"Duplicado rechazado correctamente → {e}")
        logger.advertencia(f"OP4: duplicado detectado: {e}")

    # ── Operación 5: Teléfono inválido (error esperado) ──
    subtitulo("Operación 5 — Teléfono inválido (debe fallar)")
    try:
        c_tel = Cliente("CC-1003", "Luis García", "luis@ok.com", "abc-no-es-tel")
        repo_clientes.registrar(c_tel)
        fallo("No se detectó el teléfono inválido")
    except SoftwareFJError as e:
        ok(f"Teléfono inválido rechazado → {e}")
        logger.advertencia(f"OP5: teléfono inválido: {e}")

    # Agregar un tercer cliente válido para las reservas
    try:
        c3 = Cliente("CC-2050", "Carlos Ruiz", "carlos@empresa.org", "3157890123", "natural")
        repo_clientes.registrar(c3)
        ok(f"Cliente adicional registrado: {c3.nombre}")
    except SoftwareFJError as e:
        fallo(str(e))

    info(f"Total clientes registrados: {repo_clientes.total()}")
    return repo_clientes


# ══════════════════════════════════════════════════════
# BLOQUE 2: CREACIÓN DE SERVICIOS
# ══════════════════════════════════════════════════════
def bloque_servicios(repo_servicios: RepositorioServicios):
    titulo("BLOQUE 2 — CREACIÓN DE SERVICIOS")

    # ── Operación 6: Sala válida ──
    subtitulo("Operación 6 — Sala de reuniones válida")
    try:
        sala1 = ReservaSala(
            "SALA-A1", "Sala Ejecutiva A",
            tarifa_hora=80_000,
            capacidad_max=10,
            tiene_proyector=True,
            tiene_videoconferencia=True,
        )
        repo_servicios.agregar(sala1)
        ok(f"Servicio creado: {sala1.nombre}")
        print(f"\n{sala1.descripcion_detallada()}\n")
    except SoftwareFJError as e:
        fallo(str(e))
        logger.error(f"OP6 fallida: {e}")

    # ── Operación 7: Equipo válido ──
    subtitulo("Operación 7 — Alquiler de equipo (laptop)")
    try:
        laptop = AlquilerEquipo(
            "EQ-L01", "Laptop HP ProBook",
            tarifa_hora=25_000,
            tipo_equipo="laptop",
            requiere_deposito=True,
        )
        repo_servicios.agregar(laptop)
        ok(f"Servicio creado: {laptop.nombre}")
        print(f"\n{laptop.descripcion_detallada()}\n")
    except SoftwareFJError as e:
        fallo(str(e))
        logger.error(f"OP7 fallida: {e}")

    # ── Operación 8: Asesoría válida ──
    subtitulo("Operación 8 — Asesoría especializada")
    try:
        asesoria = AsesoriaEspecializada(
            "ASE-001", "Consultoría en Ciberseguridad",
            tarifa_hora=150_000,
            area="Tecnología",
            nivel_asesor="experto",
        )
        repo_servicios.agregar(asesoria)
        ok(f"Servicio creado: {asesoria.nombre}")
        print(f"\n{asesoria.descripcion_detallada()}\n")
    except SoftwareFJError as e:
        fallo(str(e))
        logger.error(f"OP8 fallida: {e}")

    # ── Operación 9: Equipo con tipo inválido (debe fallar) ──
    subtitulo("Operación 9 — Equipo con tipo inválido (debe fallar)")
    try:
        equipo_malo = AlquilerEquipo(
            "EQ-X99", "Máquina misteriosa",
            tarifa_hora=10_000,
            tipo_equipo="ovni",   # tipo no válido
        )
        repo_servicios.agregar(equipo_malo)
        fallo("No se detectó el tipo inválido")
    except SoftwareFJError as e:
        ok(f"Tipo de equipo inválido rechazado → {e}")
        logger.advertencia(f"OP9: tipo equipo inválido: {e}")

    # ── Operación 10: Asesoría con nivel inválido (debe fallar) ──
    subtitulo("Operación 10 — Asesoría con nivel inválido (debe fallar)")
    try:
        ase_mala = AsesoriaEspecializada(
            "ASE-999", "Gurú misterioso",
            tarifa_hora=200_000,
            area="Magia",
            nivel_asesor="semidios",   # no existe
        )
        repo_servicios.agregar(ase_mala)
        fallo("No se detectó el nivel inválido")
    except SoftwareFJError as e:
        ok(f"Nivel inválido rechazado → {e}")
        logger.advertencia(f"OP10: nivel asesor inválido: {e}")

    info(f"Total servicios registrados: {repo_servicios.total()}")
    return repo_servicios


# ══════════════════════════════════════════════════════
# BLOQUE 3: GESTIÓN DE RESERVAS
# ══════════════════════════════════════════════════════
def bloque_reservas(
    repo_clientes: RepositorioClientes,
    repo_servicios: RepositorioServicios,
    repo_reservas: RepositorioReservas,
):
    titulo("BLOQUE 3 — GESTIÓN DE RESERVAS")

    ana    = repo_clientes.buscar("CC-1001")
    corp   = repo_clientes.buscar("NIT-9002")
    carlos = repo_clientes.buscar("CC-2050")
    sala   = repo_servicios.buscar("SALA-A1")
    laptop = repo_servicios.buscar("EQ-L01")
    ase    = repo_servicios.buscar("ASE-001")

    reserva1 = None

    # ── Operación 11: Reserva válida de sala ──
    subtitulo("Operación 11 — Reserva de sala válida (Ana, 3 horas)")
    try:
        reserva1 = repo_reservas.crear(ana, sala, horas=3.0, num_asistentes=6)
        ok(f"Reserva creada: {reserva1.id}")
        costo = reserva1.confirmar(incluir_iva=True, descuento=0.05)
        ok("Reserva confirmada")
        mostrar_costo(costo)
    except SoftwareFJError as e:
        fallo(f"Error: {e}")
        logger.error(f"OP11: {e}", e)

    # ── Operación 12: Reserva válida de equipo ──
    subtitulo("Operación 12 — Reserva de laptop (TechCorp, 10 horas)")
    try:
        reserva2 = repo_reservas.crear(corp, laptop, horas=10.0)
        ok(f"Reserva creada: {reserva2.id}")
        costo = reserva2.confirmar(incluir_iva=True)
        ok("Reserva confirmada")
        mostrar_costo(costo)
        reserva2.procesar()
        ok("Reserva procesada (servicio entregado)")
    except SoftwareFJError as e:
        fallo(f"Error: {e}")
        logger.error(f"OP12: {e}", e)

    # ── Operación 13: Reserva de asesoría con descuento corporativo ──
    subtitulo("Operación 13 — Asesoría (Carlos, 2h, tarifa corporativa)")
    try:
        reserva3 = repo_reservas.crear(carlos, ase, horas=2.0)
        ok(f"Reserva creada: {reserva3.id}")
        costo = reserva3.servicio.calcular_costo_corporativo(2.0, num_personas=10)
        ok("Costo corporativo calculado (sobrecarga de método)")
        mostrar_costo(costo)
        reserva3.confirmar(incluir_iva=True)
        ok("Reserva confirmada")
    except SoftwareFJError as e:
        fallo(f"Error: {e}")
        logger.error(f"OP13: {e}", e)

    # ── Operación 14: Reserva con duración fuera de rango (debe fallar) ──
    subtitulo("Operación 14 — Sala con 15h (excede límite, debe fallar)")
    try:
        r_mala = repo_reservas.crear(ana, sala, horas=15.0, num_asistentes=2)
        fallo("No se detectó la duración inválida")
    except SoftwareFJError as e:
        ok(f"Duración inválida rechazada → {e}")
        logger.advertencia(f"OP14: duración excedida: {e}")

    # ── Operación 15: Servicio no disponible (debe fallar) ──
    subtitulo("Operación 15 — Servicio deshabilitado (debe fallar)")
    try:
        sala.cambiar_disponibilidad(False)
        r_no_disp = repo_reservas.crear(ana, sala, horas=2.0, num_asistentes=3)
        fallo("No se detectó el servicio no disponible")
    except SoftwareFJError as e:
        ok(f"Servicio no disponible rechazado → {e}")
        logger.advertencia(f"OP15: servicio no disponible: {e}")
    finally:
        sala.cambiar_disponibilidad(True)  # restaurar

    # ── Operación 16: Cancelar reserva activa ──
    subtitulo("Operación 16 — Cancelar reserva de Ana")
    try:
        if reserva1:
            reserva1.cancelar("Cliente solicitó reprogramación")
            ok(f"Reserva {reserva1.id} cancelada exitosamente")
            info(f"Historial:\n{reserva1.historial_estados()}")
    except SoftwareFJError as e:
        fallo(f"Error al cancelar: {e}")
        logger.error(f"OP16: {e}", e)

    # ── Operación 17: Intentar confirmar reserva ya cancelada (debe fallar) ──
    subtitulo("Operación 17 — Confirmar reserva cancelada (debe fallar)")
    try:
        if reserva1:
            reserva1.confirmar()
            fallo("No se detectó la operación inválida")
    except SoftwareFJError as e:
        ok(f"Operación inválida rechazada → {e}")
        logger.advertencia(f"OP17: transición inválida detectada: {e}")

    # ── Operación 18: Encadenamiento de excepciones ──
    subtitulo("Operación 18 — Exceso de asistentes en sala (encadenamiento)")
    try:
        r_cap = repo_reservas.crear(corp, sala, horas=2.0, num_asistentes=50)
        fallo("No se detectó el exceso de capacidad")
    except SoftwareFJError as e:
        causa = e.__cause__
        ok(f"Exceso de capacidad rechazado → {e}")
        if causa:
            ok(f"  Causa original (encadenada): {causa}")
        logger.advertencia(f"OP18: exceso capacidad: {e}")

    # ── Operación 19: Método sobrecargado calcular_costo_simple ──
    subtitulo("Operación 19 — Cálculo simple de asesoría (sin IVA)")
    try:
        costo_simple = ase.calcular_costo_simple(1.5)
        ok(f"Costo simple de asesoría por 1.5h: ${costo_simple:,.2f}")
        logger.info(f"OP19: costo simple calculado: ${costo_simple:,.2f}")
    except SoftwareFJError as e:
        fallo(str(e))

    # ── Operación 20: Descuento inválido (debe fallar) ──
    subtitulo("Operación 20 — Descuento inválido > 100% (debe fallar)")
    try:
        r_desc = repo_reservas.crear(carlos, ase, horas=1.0)
        r_desc.confirmar(incluir_iva=True, descuento=1.5)  # 150% inválido
        fallo("No se detectó el descuento inválido")
    except SoftwareFJError as e:
        ok(f"Descuento inválido rechazado → {e}")
        logger.advertencia(f"OP20: descuento inválido: {e}")

    info(f"Total reservas creadas en el sistema: {repo_reservas.total()}")


# ══════════════════════════════════════════════════════
# BLOQUE 4: RESUMEN FINAL DEL SISTEMA
# ══════════════════════════════════════════════════════
def bloque_resumen(
    repo_clientes: RepositorioClientes,
    repo_servicios: RepositorioServicios,
    repo_reservas: RepositorioReservas,
):
    titulo("BLOQUE 4 — RESUMEN FINAL DEL SISTEMA")

    subtitulo("Clientes registrados")
    for c in repo_clientes.listar_todos():
        print(f"  • {c.describir()}")

    subtitulo("Servicios disponibles")
    for s in repo_servicios.listar_todos():
        print(f"  • {s.describir()}")

    subtitulo("Todas las reservas")
    for r in repo_reservas.listar_todas():
        print(f"\n{r.describir()}")
        print(f"  Historial:\n{r.historial_estados()}")

    subtitulo("Estadísticas")
    estados = {}
    for r in repo_reservas.listar_todas():
        estados[r.estado] = estados.get(r.estado, 0) + 1
    for estado, cnt in estados.items():
        print(f"  {estado}: {cnt} reserva(s)")

    print(f"\n  Clientes:  {repo_clientes.total()}")
    print(f"  Servicios: {repo_servicios.total()}")
    print(f"  Reservas:  {repo_reservas.total()}")


# ══════════════════════════════════════════════════════
# PUNTO DE ENTRADA PRINCIPAL
# ══════════════════════════════════════════════════════
def main():
    print("\n" + "█" * 65)
    print("█" + " " * 15 + "SOFTWARE FJ — SISTEMA INTEGRAL" + " " * 18 + "█")
    print("█" + " " * 10 + "Gestión de Clientes, Servicios y Reservas" + " " * 11 + "█")
    print("█" * 65)

    try:
        repo_clientes, repo_servicios, repo_reservas = inicializar_sistema()

        bloque_clientes(repo_clientes)
        bloque_servicios(repo_servicios)
        bloque_reservas(repo_clientes, repo_servicios, repo_reservas)
        bloque_resumen(repo_clientes, repo_servicios, repo_reservas)

        titulo("SISTEMA FINALIZADO CORRECTAMENTE")
        print("  Todos los errores fueron capturados y el sistema")
        print("  se mantuvo estable en todo momento.\n")
        print(f"  📄 Logs guardados en: logs/software_fj.log\n")
        logger.evento("=== SISTEMA FINALIZADO SIN INTERRUPCIONES ===")

    except Exception as e:
        # Captura de último recurso para errores no esperados
        logger.error(f"ERROR CATASTRÓFICO NO CONTROLADO: {e}", e)
        print(f"\n  🔴 Error crítico no controlado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
