"""
Validadores - Funciones de validación de datos
"""

import re
from typing import Tuple
from .constants import (
    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    MIN_CODIGO_LENGTH, MAX_CODIGO_LENGTH,
    MIN_PUNTAJE, MAX_PUNTAJE,
    MAX_TIEMPO_SEGUNDOS, MAX_INTERACCIONES_IA
)


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not email:
        return False, "Email es requerido"
    
    # Patrón simple de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Formato de email inválido"
    
    return True, ""


def validate_codigo(codigo: str) -> Tuple[bool, str]:
    """
    Valida código de estudiante
    
    Args:
        codigo: Código a validar
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not codigo:
        return False, "Código es requerido"
    
    if len(codigo) < MIN_CODIGO_LENGTH:
        return False, f"El código debe tener al menos {MIN_CODIGO_LENGTH} caracteres"
    
    if len(codigo) > MAX_CODIGO_LENGTH:
        return False, f"El código no puede exceder {MAX_CODIGO_LENGTH} caracteres"
    
    # Solo alfanuméricos y guiones
    if not re.match(r'^[a-zA-Z0-9-]+$', codigo):
        return False, "El código solo puede contener letras, números y guiones"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valida contraseña
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not password:
        return False, "Contraseña es requerida"
    
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"La contraseña es demasiado larga"
    
    return True, ""


def validate_puntaje(puntaje: float) -> Tuple[bool, str]:
    """
    Valida puntaje de sesión
    
    Args:
        puntaje: Puntaje a validar
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    try:
        puntaje_float = float(puntaje)
    except (ValueError, TypeError):
        return False, "El puntaje debe ser un número"
    
    if not MIN_PUNTAJE <= puntaje_float <= MAX_PUNTAJE:
        return False, f"El puntaje debe estar entre {MIN_PUNTAJE} y {MAX_PUNTAJE}"
    
    return True, ""


def validate_tiempo(tiempo_segundos: int) -> Tuple[bool, str]:
    """
    Valida tiempo de sesión
    
    Args:
        tiempo_segundos: Tiempo en segundos
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    try:
        tiempo_int = int(tiempo_segundos)
    except (ValueError, TypeError):
        return False, "El tiempo debe ser un número entero"
    
    if tiempo_int < 0:
        return False, "El tiempo no puede ser negativo"
    
    if tiempo_int > MAX_TIEMPO_SEGUNDOS:
        return False, f"El tiempo no puede exceder {MAX_TIEMPO_SEGUNDOS / 60} minutos"
    
    return True, ""


def validate_interacciones(interacciones: int) -> Tuple[bool, str]:
    """
    Valida número de interacciones con IA
    
    Args:
        interacciones: Número de interacciones
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    try:
        interacciones_int = int(interacciones)
    except (ValueError, TypeError):
        return False, "Las interacciones deben ser un número entero"
    
    if interacciones_int < 0:
        return False, "Las interacciones no pueden ser negativas"
    
    if interacciones_int > MAX_INTERACCIONES_IA:
        return False, f"Número de interacciones inusualmente alto (máx: {MAX_INTERACCIONES_IA})"
    
    return True, ""


def validate_nombre(nombre: str) -> Tuple[bool, str]:
    """
    Valida nombre de usuario
    
    Args:
        nombre: Nombre a validar
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not nombre:
        return False, "El nombre es requerido"
    
    if len(nombre.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(nombre) > 100:
        return False, "El nombre es demasiado largo"
    
    return True, ""
