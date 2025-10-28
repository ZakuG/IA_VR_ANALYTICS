"""
🔐 Auth Routes - Blueprint de Autenticación
============================================

Rutas para autenticación de usuarios:
- Login (Profesor/Estudiante)
- Register (Profesor/Estudiante)
- Logout
- Forgot Password
- Reset Password

Patrón: MVC con Service Layer
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, current_user
import pandas as pd
from datetime import datetime
import os
import secrets

from models import db, Profesor, Estudiante
from services.auth_service import AuthService
from services.email_service import EmailService
from utils.constants import (
    HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED,
    MSG_ERROR_AUTENTICACION, ROLE_PROFESOR, ROLE_ESTUDIANTE
)
from utils.logger import get_logger
from utils.extensions import get_limiter
from utils.rate_limiter import RATE_LIMITS
from utils.bot_detector import adaptive_captcha_required

# Crear blueprint
auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

# Obtener limiter
limiter = get_limiter()


@auth_bp.route('/')
def index():
    """Página principal - Redirige a dashboard si está autenticado"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('index.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registro de usuarios (Profesor/Estudiante).
    
    GET /register - Muestra formulario de registro
    POST /register - Crea nueva cuenta
    
    POST Body (JSON):
        {
            "tipo_usuario": "profesor" | "estudiante",
            "nombre": str,
            "email": str,
            "password": str,
            "confirm_password": str,
            "codigo": str (solo estudiantes)
        }
    
    Returns:
        200 OK: Formulario HTML (GET)
        201 Created: Registro exitoso (POST)
        400 Bad Request: Datos inválidos (POST)
        429 Too Many Requests: Rate limit excedido (POST)
    """
    # GET: Mostrar formulario (SIN rate limiting ni captcha)
    if request.method == 'GET':
        return render_template('register.html')
    
    # POST: Procesar registro (CON rate limiting y captcha adaptativo)
    if request.method == 'POST':
        # 🛡️ RATE LIMITING: Aplicar manualmente solo a POST
        @limiter.limit(RATE_LIMITS['register'])
        def apply_rate_limit():
            pass
        
        try:
            apply_rate_limit()
        except Exception as e:
            # Si excede rate limit, retornar error
            logger.warning(f"⚠️ Rate limit excedido en registro - IP: {request.remote_addr}")
            return jsonify({
                'success': False,
                'message': 'Demasiadas solicitudes. Por favor, intenta más tarde.',
                'error': 'rate_limit_exceeded',
                'retry_after': RATE_LIMITS['register']
            }), 429
        
        # 🤖 CAPTCHA ADAPTATIVO: Validar solo si es sospechoso
        from utils.bot_detector import BotDetector
        from flask import current_app
        
        BotDetector.record_request()
        analysis = BotDetector.is_suspicious()
        
        if analysis['suspicious']:
            current_app.logger.warning(f"🤖 Registro sospechoso (score: {analysis['score']})")
            
            recaptcha = current_app.extensions.get('recaptcha')
            if not recaptcha or not recaptcha.verify():
                BotDetector.record_failure()
                return jsonify({
                    'error': 'captcha_required',
                    'message': 'Verificación de seguridad requerida',
                    'score': analysis['score']
                }), HTTP_BAD_REQUEST
            
            BotDetector.clear_failures()
        else:
            current_app.logger.info(f"✅ Registro legítimo (score: {analysis['score']})")
        
        data = request.json
        logger.debug(f"Registro - Tipo: {data.get('tipo_usuario')}, Email: {data.get('email')}")
        
        tipo_usuario = data.get('tipo_usuario', 'profesor')
        auth_service = AuthService()
        
        try:
            if tipo_usuario == 'profesor':
                confirm_password = data.get('confirm_password') or data.get('password')
                
                resultado = auth_service.register_profesor(
                    nombre=data.get('nombre'),
                    email=data.get('email'),
                    password=data.get('password'),
                    confirm_password=confirm_password,
                    institucion=data.get('institucion')
                )
                
                return jsonify(resultado), HTTP_CREATED if resultado['success'] else HTTP_BAD_REQUEST
            
            elif tipo_usuario == 'estudiante':
                confirm_password = data.get('confirm_password') or data.get('password')
                codigo = data.get('codigo')
                email = data.get('email')
                
                # Generar código desde email si no se proporciona
                if not codigo and email:
                    codigo = email.split('@')[0].upper()
                
                if not codigo:
                    return jsonify({
                        'success': False,
                        'message': 'Se requiere código o email del estudiante'
                    }), HTTP_BAD_REQUEST
                
                resultado = auth_service.register_estudiante(
                    nombre=data.get('nombre'),
                    codigo=codigo,
                    password=data.get('password'),
                    confirm_password=confirm_password,
                    email=email
                )
                
                return jsonify(resultado), HTTP_CREATED if resultado['success'] else HTTP_BAD_REQUEST
            
            else:
                return jsonify({
                    'success': False,
                    'message': 'Tipo de usuario inválido'
                }), HTTP_BAD_REQUEST
        
        except Exception as e:
            logger.error(f"Error en registro: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error en registro: {str(e)}'
            }), HTTP_BAD_REQUEST


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login de usuarios (Profesor/Estudiante).
    
    GET /login - Muestra formulario de login
    POST /login - Valida credenciales
    
    POST Body (JSON):
        {
            "email": str (profesores),
            "codigo": str (estudiantes),
            "password": str
        }
    
    Returns:
        200 OK: Formulario HTML (GET) o Login exitoso (POST)
        401 Unauthorized: Credenciales inválidas (POST)
        429 Too Many Requests: Rate limit excedido (POST)
    """
    # GET: Mostrar formulario (SIN rate limiting ni captcha)
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST: Procesar login (CON rate limiting y captcha adaptativo)
    if request.method == 'POST':
        # 🛡️ RATE LIMITING: Aplicar manualmente solo a POST
        @limiter.limit(RATE_LIMITS['login'])
        def apply_rate_limit():
            pass
        
        try:
            apply_rate_limit()
        except Exception as e:
            # Si excede rate limit, retornar error
            logger.warning(f"⚠️ Rate limit excedido en login - IP: {request.remote_addr}")
            return jsonify({
                'success': False,
                'message': 'Demasiadas solicitudes. Por favor, intenta más tarde.',
                'error': 'rate_limit_exceeded',
                'retry_after': RATE_LIMITS['login']
            }), 429
        
        # 🤖 CAPTCHA ADAPTATIVO: Validar solo si es sospechoso
        from utils.bot_detector import BotDetector
        from flask import current_app
        
        BotDetector.record_request()
        analysis = BotDetector.is_suspicious()
        
        if analysis['suspicious']:
            current_app.logger.warning(f"🤖 Login sospechoso (score: {analysis['score']})")
            
            recaptcha = current_app.extensions.get('recaptcha')
            if not recaptcha or not recaptcha.verify():
                BotDetector.record_failure()
                return jsonify({
                    'error': 'captcha_required',
                    'message': 'Verificación de seguridad requerida',
                    'score': analysis['score']
                }), HTTP_BAD_REQUEST
            
            BotDetector.clear_failures()
        else:
            current_app.logger.info(f"✅ Login legítimo (score: {analysis['score']})")
        
        data = request.json
        logger.debug(f"Login - Email/Código: {data.get('email') or data.get('codigo')}")
        
        auth_service = AuthService()
        
        # Intentar login como profesor (si tiene email)
        if 'email' in data:
            resultado = auth_service.login_profesor(
                email=data.get('email'),
                password=data.get('password')
            )
            
            if resultado['success']:
                profesor = Profesor.query.get(resultado['user']['id'])
                login_user(profesor)
                logger.info(f"Login exitoso - Profesor: {profesor.email}")
                return jsonify({'success': True, 'tipo': ROLE_PROFESOR}), HTTP_OK
        
        # Intentar login como estudiante (código o email)
        codigo_o_email = data.get('codigo') or data.get('email')
        
        if codigo_o_email:
            # Login por código
            resultado = auth_service.login_estudiante(
                codigo=codigo_o_email,
                password=data.get('password')
            )
            
            # Si falla y parece email, intentar buscar por email
            if not resultado['success'] and '@' in codigo_o_email:
                estudiante = Estudiante.query.filter_by(email=codigo_o_email).first()
                if estudiante and estudiante.check_password(data.get('password')):
                    login_user(estudiante)
                    logger.info(f"Login exitoso - Estudiante: {estudiante.email}")
                    return jsonify({'success': True, 'tipo': ROLE_ESTUDIANTE}), HTTP_OK
            
            # Login exitoso por código
            if resultado['success']:
                estudiante = Estudiante.query.get(resultado['user']['id'])
                login_user(estudiante)
                logger.info(f"Login exitoso - Estudiante: {estudiante.codigo}")
                return jsonify({'success': True, 'tipo': ROLE_ESTUDIANTE}), HTTP_OK
        
        # Credenciales inválidas
        logger.warning(f"Login fallido - Credenciales inválidas")
        return jsonify({
            'success': False,
            'message': MSG_ERROR_AUTENTICACION
        }), HTTP_UNAUTHORIZED


@auth_bp.route('/logout')
def logout():
    """
    Cierra sesión del usuario actual.
    
    Returns:
        Redirect: Redirige a la página de login
    """
    if current_user.is_authenticated:
        logger.info(f"Logout - Usuario: {current_user.email if hasattr(current_user, 'email') else current_user.codigo}")
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Solicitud de recuperación de contraseña.
    
    POST /forgot-password
    Body (JSON):
        {
            "email": str
        }
    
    Returns:
        200 OK: Correo enviado (o mensaje genérico por seguridad)
    """
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        
        # Buscar usuario (profesor o estudiante)
        profesor = Profesor.query.filter_by(email=email).first()
        estudiante = Estudiante.query.filter_by(email=email).first()
        usuario = profesor or estudiante
        
        if usuario:
            # Generar token seguro
            token = secrets.token_urlsafe(32)
            usuario.reset_token = token
            usuario.reset_token_expiry = datetime.utcnow() + pd.Timedelta(hours=1)
            db.session.commit()
            
            # Generar enlace de recuperación
            base_url = os.getenv('APP_BASE_URL', 'http://127.0.0.1:5000')
            reset_link = f"{base_url}/reset-password/{token}"
            
            # Enviar correo
            from flask import current_app
            email_service = EmailService(mail_instance=current_app.extensions['mail'])
            resultado_email = email_service.send_password_reset_email(
                email=email,
                reset_link=reset_link,
                nombre=usuario.nombre
            )
            
            if resultado_email['success']:
                logger.info(f"Correo recuperación enviado a {email}")
            else:
                logger.error(f"Error enviando correo a {email}: {resultado_email['message']}")
        
        # Por seguridad, siempre retornar éxito
        return jsonify({
            'success': True,
            'message': 'Si el email existe, recibirás instrucciones para recuperar tu contraseña'
        })
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Restablece la contraseña con un token válido.
    
    POST /reset-password/<token>
    Body (JSON):
        {
            "password": str,
            "confirm_password": str
        }
    
    Returns:
        200 OK: Contraseña actualizada
        400 Bad Request: Token inválido/expirado
    """
    if request.method == 'POST':
        data = request.json
        
        # Validar que se reciban los datos necesarios
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos no proporcionados'
            }), HTTP_BAD_REQUEST
        
        new_password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Validar que los campos existan
        if not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'message': 'Ambas contraseñas son requeridas'
            }), HTTP_BAD_REQUEST
        
        # Validar confirmación
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }), HTTP_BAD_REQUEST
        
        # Buscar usuario por token
        profesor = Profesor.query.filter_by(reset_token=token).first()
        estudiante = Estudiante.query.filter_by(reset_token=token).first()
        usuario = profesor or estudiante
        
        if not usuario or usuario.reset_token_expiry < datetime.utcnow():
            return jsonify({
                'success': False,
                'message': 'Token inválido o expirado'
            }), HTTP_BAD_REQUEST
        
        # Actualizar contraseña
        usuario.set_password(new_password)
        usuario.reset_token = None
        usuario.reset_token_expiry = None
        db.session.commit()
        
        logger.info(f"Contraseña restablecida - Usuario: {usuario.email if hasattr(usuario, 'email') else usuario.codigo}")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        })
    
    # Verificar token en GET
    profesor = Profesor.query.filter_by(reset_token=token).first()
    estudiante = Estudiante.query.filter_by(reset_token=token).first()
    usuario = profesor or estudiante
    
    if not usuario or usuario.reset_token_expiry < datetime.utcnow():
        return render_template('reset_password.html', token_valido=False)
    
    return render_template('reset_password.html', token=token, token_valido=True)
