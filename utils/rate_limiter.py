"""
🛡️ Rate Limiting Configuration
================================

Configuración de límites de tasa para proteger contra ataques de spam/bots
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuración de límites por ruta
RATE_LIMITS = {
    # Rutas de autenticación (más restrictivas)
    'register': "3 per hour",  # Máximo 3 registros por hora por IP
    'login': "10 per minute",  # Máximo 10 intentos de login por minuto
    'forgot_password': "3 per hour",  # Máximo 3 solicitudes de recuperación por hora
    
    # Rutas del dashboard (más permisivas)
    'dashboard': "100 per minute",
    'analytics': "50 per minute",
    
    # Rutas de API
    'api_general': "60 per minute",
}

# Límites por defecto para toda la aplicación
DEFAULT_LIMITS = ["200 per day", "50 per hour"]

# Mensajes de error personalizados
RATE_LIMIT_MESSAGES = {
    'es': "Demasiadas solicitudes. Por favor, intenta más tarde.",
    'en': "Too many requests. Please try again later."
}


def get_limiter_config():
    """Retorna configuración del limiter"""
    return {
        'key_func': get_remote_address,
        'default_limits': DEFAULT_LIMITS,
        'storage_uri': 'memory://',
        'strategy': 'fixed-window',
        'swallow_errors': True  # No romper app si hay error en limiter
    }


def rate_limit_exceeded_handler(e):
    """Handler personalizado cuando se excede el límite"""
    return {
        'success': False,
        'message': RATE_LIMIT_MESSAGES['es'],
        'error': 'rate_limit_exceeded',
        'retry_after': e.description
    }, 429
