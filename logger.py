"""
logger.py - Sistema de registro de eventos y errores - Software FJ
"""

import os
import traceback
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "software_fj.log")


def _asegurar_directorio():
    directorio = os.path.dirname(LOG_PATH)
    if not os.path.exists(directorio):
        os.makedirs(directorio)


def _escribir(nivel: str, mensaje: str, excepcion: Exception = None):
    _asegurar_directorio()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lineas = [f"[{timestamp}] [{nivel}] {mensaje}"]
    if excepcion:
        tb = traceback.format_exc()
        if tb.strip() != "NoneType: None":
            lineas.append(f"  TRAZA: {tb.strip()}")
    entrada = "\n".join(lineas) + "\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entrada)
    # También imprimimos en consola para visibilidad en demo
    print(f"  📋 LOG [{nivel}]: {mensaje}")


def info(mensaje: str):
    _escribir("INFO", mensaje)


def advertencia(mensaje: str, excepcion: Exception = None):
    _escribir("ADVERTENCIA", mensaje, excepcion)


def error(mensaje: str, excepcion: Exception = None):
    _escribir("ERROR", mensaje, excepcion)


def evento(mensaje: str):
    _escribir("EVENTO", mensaje)


def leer_logs() -> str:
    """Retorna el contenido completo del archivo de logs."""
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(Sin registros aún)"
