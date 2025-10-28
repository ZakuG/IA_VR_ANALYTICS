"""
🔒 Google reCAPTCHA v2 Integration
===================================

Implementación manual de reCAPTCHA v2 compatible con Flask 3.x
"""

import requests
from flask import current_app, request
from functools import wraps


class ReCaptcha:
    """Clase para manejar validación de reCAPTCHA v2"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa la extensión con la app de Flask"""
        self.app = app
        
        # Guardar la instancia en app.extensions para uso posterior
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['recaptcha'] = self
        
        # Valores por defecto
        app.config.setdefault('RECAPTCHA_ENABLED', False)
        app.config.setdefault('RECAPTCHA_SITE_KEY', '')
        app.config.setdefault('RECAPTCHA_SECRET_KEY', '')
        app.config.setdefault('RECAPTCHA_THEME', 'light')
        app.config.setdefault('RECAPTCHA_TYPE', 'image')
        app.config.setdefault('RECAPTCHA_SIZE', 'normal')
        
        # Registrar context processor
        @app.context_processor
        def recaptcha_context():
            """Hace available la configuración de reCAPTCHA en templates"""
            return {
                'recaptcha': self,
                'RECAPTCHA_ENABLED': app.config.get('RECAPTCHA_ENABLED', False),
                'RECAPTCHA_SITE_KEY': app.config.get('RECAPTCHA_SITE_KEY', '')
            }
    
    def verify(self, recaptcha_response=None, remote_ip=None):
        """
        Verifica la respuesta del reCAPTCHA
        
        Args:
            recaptcha_response: Token de respuesta del cliente (opcional, se obtiene de request)
            remote_ip: IP del cliente (opcional, se obtiene de request)
        
        Returns:
            bool: True si la verificación fue exitosa
        """
        # Si reCAPTCHA está deshabilitado, siempre retorna True
        if not current_app.config.get('RECAPTCHA_ENABLED', False):
            return True
        
        # Obtener token de respuesta
        if recaptcha_response is None:
            recaptcha_response = request.form.get('g-recaptcha-response') or \
                                request.json.get('recaptcha_token') if request.is_json else None
        
        if not recaptcha_response:
            return False
        
        # Obtener IP del cliente
        if remote_ip is None:
            remote_ip = request.remote_addr
        
        # Hacer request a Google para verificar
        secret_key = current_app.config.get('RECAPTCHA_SECRET_KEY', '')
        
        if not secret_key:
            current_app.logger.warning("RECAPTCHA_SECRET_KEY no configurada")
            return True  # Permitir si no está configurada
        
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        
        payload = {
            'secret': secret_key,
            'response': recaptcha_response,
            'remoteip': remote_ip
        }
        
        try:
            response = requests.post(verify_url, data=payload, timeout=5)
            result = response.json()
            
            return result.get('success', False)
        
        except Exception as e:
            current_app.logger.error(f"Error verificando reCAPTCHA: {e}")
            return False
    
    def get_html(self):
        """
        Retorna el HTML del widget de reCAPTCHA
        
        Returns:
            str: HTML del widget
        """
        if not current_app.config.get('RECAPTCHA_ENABLED', False):
            return ''
        
        site_key = current_app.config.get('RECAPTCHA_SITE_KEY', '')
        theme = current_app.config.get('RECAPTCHA_THEME', 'light')
        size = current_app.config.get('RECAPTCHA_SIZE', 'normal')
        
        return f'''<div class="g-recaptcha" 
                    data-sitekey="{site_key}" 
                    data-theme="{theme}" 
                    data-size="{size}">
                </div>'''


def recaptcha_required(f):
    """
    Decorador para requerir reCAPTCHA en una ruta
    
    Usage:
        @app.route('/submit', methods=['POST'])
        @recaptcha_required
        def submit():
            # Tu código aquí
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Solo validar en requests POST (GET requests son para mostrar el formulario)
        if request.method != 'POST':
            return f(*args, **kwargs)
        
        # Si reCAPTCHA está deshabilitado, continúa normalmente
        if not current_app.config.get('RECAPTCHA_ENABLED', False):
            return f(*args, **kwargs)
        
        # Obtener la instancia de ReCaptcha almacenada en app.extensions
        recaptcha = current_app.extensions.get('recaptcha')
        
        # Si no hay instancia (no debería pasar), continuar normalmente
        if not recaptcha:
            current_app.logger.warning("ReCaptcha no está inicializado en app.extensions")
            return f(*args, **kwargs)
        
        # Verificar reCAPTCHA
        if not recaptcha.verify():
            from flask import jsonify
            return jsonify({
                'success': False,
                'message': 'Por favor, completa el reCAPTCHA',
                'error': 'recaptcha_failed'
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function
