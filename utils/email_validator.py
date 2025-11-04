"""
Email Configuration Validator
Valida que la configuración de correo electrónico sea correcta
"""

import os
import logging

logger = logging.getLogger(__name__)


def validate_email_config() -> dict:
    """
    Valida que todas las variables de entorno necesarias para correo estén configuradas
    
    Returns:
        dict: {
            'configured': bool,
            'warnings': list,
            'errors': list
        }
    """
    warnings = []
    errors = []
    
    # Variables requeridas
    required_vars = ['MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SERVER']
    
    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Variable {var} no configurada")
    
    # Variables opcionales pero recomendadas
    if not os.getenv('MAIL_DEFAULT_SENDER'):
        warnings.append("MAIL_DEFAULT_SENDER no configurada, se usará MAIL_USERNAME")
    
    # Validar puerto
    mail_port = os.getenv('MAIL_PORT', '587')
    if mail_port not in ['587', '465', '25']:
        warnings.append(f"MAIL_PORT={mail_port} es inusual (común: 587, 465, 25)")
    
    # Validar TLS/SSL
    use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    use_ssl = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    
    if use_tls and use_ssl:
        errors.append("MAIL_USE_TLS y MAIL_USE_SSL no pueden estar ambos en True")
    
    if not use_tls and not use_ssl and mail_port == '587':
        warnings.append("Puerto 587 generalmente requiere TLS")
    
    configured = len(errors) == 0
    
    result = {
        'configured': configured,
        'warnings': warnings,
        'errors': errors
    }
    
    # Loguear resultado
    if configured:
        logger.info("✅ Configuración de correo validada correctamente")
        if warnings:
            for warning in warnings:
                logger.warning(f"⚠️ {warning}")
    else:
        logger.error("❌ Configuración de correo inválida")
        for error in errors:
            logger.error(f"❌ {error}")
    
    return result


def get_email_config_status() -> str:
    """
    Retorna un string con el estado de la configuración de correo
    
    Returns:
        str: Mensaje describiendo el estado
    """
    validation = validate_email_config()
    
    if validation['configured']:
        return f"✅ Email configurado correctamente ({len(validation['warnings'])} advertencias)"
    else:
        return f"❌ Email NO configurado ({len(validation['errors'])} errores)"
