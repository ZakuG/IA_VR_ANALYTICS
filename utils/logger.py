"""
Configuración centralizada de logging para VR Analytics
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app):
    """
    Configura el sistema de logging de la aplicación.
    
    Niveles:
    - DEBUG: Información detallada para diagnóstico
    - INFO: Confirmación de que las cosas funcionan como se esperaba
    - WARNING: Indica que algo inesperado ocurrió
    - ERROR: Error serio, la aplicación no pudo realizar alguna función
    - CRITICAL: Error muy serio, la aplicación puede no poder continuar
    """
    
    # Determinar nivel según modo debug
    if app.config.get('DEBUG', False):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Crear logger
    logger = logging.getLogger('vr_analytics')
    logger.setLevel(log_level)
    
    # Evitar duplicados
    if logger.handlers:
        return logger
    
    # Formato de logs
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para consola con encoding UTF-8
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    # Forzar encoding UTF-8 en Windows para soportar emojis
    if hasattr(console_handler.stream, 'reconfigure'):
        console_handler.stream.reconfigure(encoding='utf-8', errors='replace')
    logger.addHandler(console_handler)
    
    # Handler para archivo (solo en producción)
    if not app.config.get('TESTING', False):
        # Crear directorio de logs si no existe
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = RotatingFileHandler(
            'logs/vr_analytics.log',
            maxBytes=10240000,  # 10MB
            backupCount=10,
            encoding='utf-8'  # Soporte UTF-8 en archivos de log
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name='vr_analytics'):
    """Obtiene una instancia del logger configurado."""
    return logging.getLogger(name)
