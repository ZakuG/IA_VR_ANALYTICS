"""
🔌 Flask Extensions
===================

Extensiones de Flask inicializadas globalmente
"""

from flask_limiter import Limiter

# Instancia global del limiter (será inicializada en app.py)
limiter = None


def init_limiter(app, limiter_config):
    """
    Inicializa el rate limiter
    
    Args:
        app: Instancia de Flask
        limiter_config: Configuración del limiter
    
    Returns:
        Limiter instance
    """
    global limiter
    limiter = Limiter(app=app, **limiter_config)
    return limiter


def get_limiter():
    """Obtiene la instancia del limiter"""
    return limiter
