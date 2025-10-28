"""
🤖 Bot Detection System
========================

Sistema de detección de bots basado en análisis de comportamiento.
Solo muestra reCAPTCHA cuando detecta actividad sospechosa.

Estrategia Multi-Capa:
1. Análisis de comportamiento (velocidad, patrones)
2. Fingerprinting de navegador
3. reCAPTCHA adaptativo (solo si es necesario)
"""

import time
from datetime import datetime, timedelta
from flask import request, session
from collections import defaultdict
import hashlib


class BotDetector:
    """
    Detector de bots basado en análisis de comportamiento.
    
    Señales de alerta:
    - Velocidad de formulario < 2 segundos
    - User-Agent sospechoso (Go-http-client, curl, etc.)
    - Sin JavaScript habilitado
    - Múltiples requests desde misma IP
    - Patrones de tipeo no humanos
    """
    
    # Almacenamiento en memoria (para producción usar Redis)
    _request_history = defaultdict(list)
    _failed_attempts = defaultdict(int)
    
    # User-Agents conocidos de bots
    BOT_USER_AGENTS = [
        'go-http-client',
        'curl',
        'wget',
        'python-requests',
        'bot',
        'crawler',
        'spider',
        'scraper'
    ]
    
    @classmethod
    def is_suspicious(cls, check_js=True, check_timing=True, check_ua=True):
        """
        Determina si el request actual es sospechoso.
        
        Args:
            check_js: Verificar si JavaScript está habilitado
            check_timing: Verificar tiempo de llenado de formulario
            check_ua: Verificar User-Agent
        
        Returns:
            dict: {'suspicious': bool, 'reasons': list, 'score': float}
        """
        suspicious_score = 0
        reasons = []
        
        # 1. Verificar User-Agent
        if check_ua:
            ua = request.headers.get('User-Agent', '').lower()
            if any(bot in ua for bot in cls.BOT_USER_AGENTS):
                suspicious_score += 50
                reasons.append(f"Bot User-Agent detectado: {ua[:50]}")
        
        # 2. Verificar JavaScript
        if check_js:
            js_enabled = session.get('js_enabled', False)
            if not js_enabled:
                suspicious_score += 30
                reasons.append("JavaScript no detectado")
        
        # 3. Verificar velocidad de llenado de formulario
        if check_timing:
            form_start = session.get('form_start_time')
            if form_start:
                elapsed = time.time() - form_start
                if elapsed < 2:  # Menos de 2 segundos = sospechoso
                    suspicious_score += 40
                    reasons.append(f"Formulario llenado muy rápido: {elapsed:.2f}s")
        
        # 4. Verificar frecuencia de requests por IP
        ip = cls._get_client_ip()
        recent_requests = cls._get_recent_requests(ip, minutes=5)
        if len(recent_requests) > 10:  # Más de 10 requests en 5 min
            suspicious_score += 40
            reasons.append(f"Demasiados requests desde IP: {len(recent_requests)}")
        
        # 5. Verificar historial de fallos
        failed_count = cls._failed_attempts.get(ip, 0)
        if failed_count > 3:
            suspicious_score += 30
            reasons.append(f"Múltiples intentos fallidos: {failed_count}")
        
        # 6. Verificar ausencia de headers comunes
        common_headers = ['Accept-Language', 'Accept-Encoding', 'Connection']
        missing_headers = [h for h in common_headers if not request.headers.get(h)]
        if len(missing_headers) >= 2:
            suspicious_score += 20
            reasons.append(f"Headers faltantes: {missing_headers}")
        
        return {
            'suspicious': suspicious_score >= 60,  # Umbral: 60 puntos
            'reasons': reasons,
            'score': min(suspicious_score, 100),
            'require_captcha': suspicious_score >= 60
        }
    
    @classmethod
    def mark_form_start(cls):
        """Marca el inicio del llenado de formulario"""
        session['form_start_time'] = time.time()
    
    @classmethod
    def mark_js_enabled(cls):
        """Marca que JavaScript está habilitado"""
        session['js_enabled'] = True
    
    @classmethod
    def record_request(cls):
        """Registra el request actual"""
        ip = cls._get_client_ip()
        cls._request_history[ip].append(time.time())
    
    @classmethod
    def record_failure(cls):
        """Registra un intento fallido"""
        ip = cls._get_client_ip()
        cls._failed_attempts[ip] += 1
    
    @classmethod
    def clear_failures(cls):
        """Limpia los intentos fallidos tras login exitoso"""
        ip = cls._get_client_ip()
        cls._failed_attempts[ip] = 0
    
    @classmethod
    def _get_client_ip(cls):
        """Obtiene la IP real del cliente (considerando proxies)"""
        # Prioridad: X-Forwarded-For > X-Real-IP > remote_addr
        if request.headers.get('X-Forwarded-For'):
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        if request.headers.get('X-Real-IP'):
            return request.headers['X-Real-IP']
        return request.remote_addr
    
    @classmethod
    def _get_recent_requests(cls, ip, minutes=5):
        """Obtiene requests recientes de una IP"""
        cutoff = time.time() - (minutes * 60)
        requests = cls._request_history.get(ip, [])
        # Limpiar requests antiguos
        recent = [r for r in requests if r > cutoff]
        cls._request_history[ip] = recent
        return recent
    
    @classmethod
    def get_fingerprint(cls):
        """
        Genera un fingerprint del navegador/cliente.
        Combina: IP + User-Agent + Accept-Language
        """
        ip = cls._get_client_ip()
        ua = request.headers.get('User-Agent', '')
        lang = request.headers.get('Accept-Language', '')
        
        fingerprint_string = f"{ip}:{ua}:{lang}"
        return hashlib.md5(fingerprint_string.encode()).hexdigest()


def adaptive_captcha_required(f):
    """
    Decorador que solo requiere reCAPTCHA si detecta comportamiento sospechoso.
    
    Uso:
        @auth_bp.route('/login', methods=['POST'])
        @adaptive_captcha_required
        def login():
            # Tu código aquí
    """
    from functools import wraps
    from flask import jsonify, current_app
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Solo aplicar en POST
        if request.method != 'POST':
            return f(*args, **kwargs)
        
        # Registrar request
        BotDetector.record_request()
        
        # Análisis de comportamiento
        analysis = BotDetector.is_suspicious()
        
        # Si NO es sospechoso, permitir sin reCAPTCHA
        if not analysis['suspicious']:
            current_app.logger.info(f"Request legítimo detectado (score: {analysis['score']})")
            return f(*args, **kwargs)
        
        # Si ES sospechoso, REQUERIR reCAPTCHA
        current_app.logger.warning(
            f"⚠️ Comportamiento sospechoso detectado (score: {analysis['score']}): "
            f"{', '.join(analysis['reasons'])}"
        )
        
        # Verificar si reCAPTCHA está habilitado
        if not current_app.config.get('RECAPTCHA_ENABLED', False):
            # Si reCAPTCHA está deshabilitado, permitir pero registrar
            current_app.logger.warning("reCAPTCHA deshabilitado - permitiendo request sospechoso")
            return f(*args, **kwargs)
        
        # Obtener instancia de ReCaptcha
        recaptcha = current_app.extensions.get('recaptcha')
        if not recaptcha:
            return f(*args, **kwargs)
        
        # VALIDAR reCAPTCHA (solo si es sospechoso)
        if not recaptcha.verify():
            BotDetector.record_failure()
            return jsonify({
                'success': False,
                'message': 'Verificación de seguridad requerida. Por favor, completa el reCAPTCHA.',
                'error': 'captcha_required',
                'suspicious_score': analysis['score'],
                'reasons': analysis['reasons']
            }), 400
        
        # reCAPTCHA verificado exitosamente
        current_app.logger.info("✅ reCAPTCHA verificado para request sospechoso")
        BotDetector.clear_failures()
        
        return f(*args, **kwargs)
    
    return decorated_function


# Helper para frontend
def get_captcha_requirement():
    """
    Endpoint helper para que el frontend sepa si debe mostrar reCAPTCHA.
    
    Returns:
        dict: {'show_captcha': bool, 'reason': str}
    """
    analysis = BotDetector.is_suspicious(check_timing=False)  # No check timing aún
    
    return {
        'show_captcha': analysis['suspicious'],
        'reason': 'Verificación de seguridad requerida' if analysis['suspicious'] else None,
        'score': analysis['score']
    }
