"""
Decoradores - Funciones decoradoras para routes
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from .constants import ROLE_ESTUDIANTE, ROLE_PROFESOR, MSG_ERROR_PERMISOS


def login_required_profesor(f):
    """
    Decorador que requiere que el usuario sea un profesor autenticado
    
    Usage:
        @app.route('/ruta-protegida')
        @login_required_profesor
        def ruta_protegida():
            # Solo accesible para profesores autenticados
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session.get('user_type') != ROLE_PROFESOR:
            flash(MSG_ERROR_PERMISOS, 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def login_required_estudiante(f):
    """
    Decorador que requiere que el usuario sea un estudiante autenticado
    
    Usage:
        @app.route('/ruta-protegida')
        @login_required_estudiante
        def ruta_protegida():
            # Solo accesible para estudiantes autenticados
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session.get('user_type') != ROLE_ESTUDIANTE:
            flash(MSG_ERROR_PERMISOS, 'error')
            return redirect(url_for('login_estudiante'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """
    Decorador genérico que requiere autenticación (profesor o estudiante)
    
    Usage:
        @app.route('/ruta-protegida')
        @login_required
        def ruta_protegida():
            # Accesible para cualquier usuario autenticado
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def validate_json(required_fields):
    """
    Decorador que valida que el request tenga JSON con campos requeridos
    
    Args:
        required_fields: Lista de campos requeridos
        
    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @validate_json(['campo1', 'campo2'])
        def endpoint():
            # request.json garantiza tener campo1 y campo2
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type debe ser application/json'
                }), 400
            
            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'message': f'Campos faltantes: {", ".join(missing_fields)}'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
