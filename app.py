# app.py - Aplicación Flask con arquitectura POO profesional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Importar modelos y configuración de DB
from models import db, bcrypt, Profesor, Estudiante, Sesion

# Importar servicios, repositorios y utilidades
from services.analytics_service import AnalyticsService
from services.session_service import SessionService
from services.auth_service import AuthService
from utils.decorators import login_required_profesor, login_required_estudiante, validate_json
from utils.validators import validate_email, validate_codigo, validate_password, validate_puntaje
from utils.constants import (
    MIN_PASSWORD_LENGTH, MAX_PUNTAJE, MIN_PUNTAJE,
    HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_NOT_FOUND,
    MSG_REGISTRO_EXITOSO, MSG_LOGIN_EXITOSO, MSG_ERROR_AUTENTICACION,
    ROLE_PROFESOR, ROLE_ESTUDIANTE
)

# Configuración de Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vr_analytics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones con la app
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario por su ID para Flask-Login"""
    if user_id.startswith('profesor_'):
        return Profesor.query.get(int(user_id.split('_')[1]))
    elif user_id.startswith('estudiante_'):
        return Estudiante.query.get(int(user_id.split('_')[1]))
    return None

# ============================================
# RUTAS DE LA APLICACIÓN
# ============================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de usuarios usando AuthService"""
    if request.method == 'POST':
        data = request.json
        
        # Debug: Ver qué datos llegan
        print("DEBUG - Datos recibidos en /register:", data)
        
        tipo_usuario = data.get('tipo_usuario', 'profesor')
        
        auth_service = AuthService()
        
        try:
            if tipo_usuario == 'profesor':
                # Si no viene confirm_password, usar password
                confirm_password = data.get('confirm_password') or data.get('password')
                
                resultado = auth_service.register_profesor(
                    nombre=data.get('nombre'),
                    email=data.get('email'),
                    password=data.get('password'),
                    confirm_password=confirm_password
                )
                
                if resultado['success']:
                    return jsonify(resultado), HTTP_CREATED
                else:
                    return jsonify(resultado), HTTP_BAD_REQUEST
            
            elif tipo_usuario == 'estudiante':
                # Si no viene confirm_password, usar password
                confirm_password = data.get('confirm_password') or data.get('password')
                
                # El código puede venir explícito o generarse desde el email
                codigo = data.get('codigo')
                email = data.get('email')
                
                if not codigo and email:
                    # Generar código desde email (ejemplo: smacheoa@correo.uss.cl → SMACHEOA)
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
                    email=email  # Pasar email también
                )
                
                if resultado['success']:
                    return jsonify(resultado), HTTP_CREATED
                else:
                    return jsonify(resultado), HTTP_BAD_REQUEST
            else:
                return jsonify({
                    'success': False, 
                    'message': 'Tipo de usuario inválido'
                }), HTTP_BAD_REQUEST
        
        except Exception as e:
            return jsonify({
                'success': False, 
                'message': f'Error en registro: {str(e)}'
            }), HTTP_BAD_REQUEST
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios usando AuthService"""
    if request.method == 'POST':
        data = request.json
        
        # Debug: Ver qué datos llegan
        print("DEBUG - Datos recibidos en /login:", data)
        
        auth_service = AuthService()
        
        # Intentar login como profesor primero (si tiene email)
        if 'email' in data:
            resultado = auth_service.login_profesor(
                email=data.get('email'),
                password=data.get('password')
            )
            
            if resultado['success']:
                profesor = Profesor.query.get(resultado['user']['id'])
                login_user(profesor)
                return jsonify({'success': True, 'tipo': ROLE_PROFESOR}), HTTP_OK
        
        # Intentar login como estudiante (por codigo o email)
        codigo_o_email = data.get('codigo') or data.get('email')
        
        if codigo_o_email:
            # Primero intentar por código
            resultado = auth_service.login_estudiante(
                codigo=codigo_o_email,
                password=data.get('password')
            )
            
            # Si falla y parece ser un email, buscar estudiante por email
            if not resultado['success'] and '@' in codigo_o_email:
                estudiante = Estudiante.query.filter_by(email=codigo_o_email).first()
                if estudiante and estudiante.check_password(data.get('password')):
                    login_user(estudiante)
                    return jsonify({'success': True, 'tipo': ROLE_ESTUDIANTE}), HTTP_OK
            
            # Si tuvo éxito el login por código
            if resultado['success']:
                estudiante = Estudiante.query.get(resultado['user']['id'])
                login_user(estudiante)
                return jsonify({'success': True, 'tipo': ROLE_ESTUDIANTE}), HTTP_OK
        
        # Credenciales inválidas
        return jsonify({
            'success': False, 
            'message': MSG_ERROR_AUTENTICACION
        }), HTTP_UNAUTHORIZED
    
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        
        # Buscar usuario (profesor o estudiante)
        profesor = Profesor.query.filter_by(email=email).first()
        estudiante = Estudiante.query.filter_by(email=email).first()
        
        usuario = profesor or estudiante
        
        if usuario:
            # Generar token simple (en producción usar algo más seguro)
            import secrets
            token = secrets.token_urlsafe(32)
            usuario.reset_token = token
            usuario.reset_token_expiry = datetime.utcnow() + pd.Timedelta(hours=1)
            db.session.commit()
            
            # En producción, enviar email con el token
            # Por ahora, retornar el token (solo para desarrollo)
            reset_link = url_for('reset_password', token=token, _external=True)
            return jsonify({
                'success': True, 
                'message': 'Se ha generado un enlace de recuperación',
                'reset_link': reset_link  # En producción, esto se enviaría por email
            })
        
        # Por seguridad, siempre retornar éxito aunque el email no exista
        return jsonify({'success': True, 'message': 'Si el email existe, recibirás instrucciones'})
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        data = request.json
        new_password = data.get('password')
        
        # Buscar usuario por token
        profesor = Profesor.query.filter_by(reset_token=token).first()
        estudiante = Estudiante.query.filter_by(reset_token=token).first()
        
        usuario = profesor or estudiante
        
        if not usuario or usuario.reset_token_expiry < datetime.utcnow():
            return jsonify({'success': False, 'message': 'Token inválido o expirado'}), 400
        
        # Actualizar contraseña
        usuario.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        usuario.reset_token = None
        usuario.reset_token_expiry = None
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada exitosamente'})
    
    return render_template('reset_password.html', token=token)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Redirigir según tipo de usuario
    if isinstance(current_user, Profesor):
        return render_template('dashboard.html', profesor=current_user)
    else:
        return render_template('dashboard_estudiante.html', estudiante=current_user)

@app.route('/dashboard/manual-entry')
@login_required
def manual_entry():
    """Página para registro manual de sesiones (solo profesores)"""
    if not isinstance(current_user, Profesor):
        return redirect(url_for('dashboard'))
    return render_template('manual_entry.html')

@app.route('/api/analytics')
@login_required
def get_analytics():
    """Analytics para profesor usando AnalyticsService"""
    import time
    inicio = time.time()
    print(f"🔵 Iniciando /api/analytics para profesor ID={current_user.id if hasattr(current_user, 'id') else 'N/A'}")
    
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False, 
            'message': 'Solo para profesores'
        }), HTTP_FORBIDDEN
    
    try:
        analytics_service = AnalyticsService()
        print(f"  ⏱️ Llamando a get_analytics_profesor...")
        resultado = analytics_service.get_analytics_profesor(current_user.id)
        
        duracion = time.time() - inicio
        print(f"✅ /api/analytics completado en {duracion:.2f}s")
        
        if resultado.get('success', True):
            return jsonify(resultado), HTTP_OK
        else:
            return jsonify(resultado), HTTP_OK
            
    except Exception as e:
        import traceback
        duracion = time.time() - inicio
        print(f"❌ Error en analytics después de {duracion:.2f}s:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'message': 'Error al procesar los datos',
            'estadisticas': {'general': {}},
            'por_maqueta': {},
            'correlaciones': {},
            'estudiantes_riesgo': [],
            'ranking': [],
            'clustering': {},
            'prediccion': {},
            'insights': [],
            'visualizacion': {
                'distribucion_puntajes': {},
                'puntajes_por_maqueta': {},
                'tiempos_por_maqueta': {},
                'tendencia_temporal': {'fechas': [], 'puntajes': []},
                'scatter_tiempo_puntaje': {'tiempo': [], 'puntaje': [], 'maqueta': []}
            },
            'ml_clasificacion': {'modelo_disponible': False},
            'ml_clustering': {},
            'ml_correlaciones': {'disponible': False}
        }), HTTP_OK

@app.route('/api/estudiantes', methods=['GET', 'POST'])
@login_required
def estudiantes():
    """Endpoint para gestionar estudiantes del profesor usando AuthService"""
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False, 
            'message': 'Solo para profesores'
        }), HTTP_FORBIDDEN
    
    if request.method == 'POST':
        data = request.json
        auth_service = AuthService()
        
        # Inscribir estudiante existente con el profesor
        resultado = auth_service.inscribir_estudiante_profesor(
            estudiante_codigo=data.get('codigo'),
            profesor_id=current_user.id
        )
        
        if resultado['success']:
            return jsonify(resultado), HTTP_CREATED
        else:
            return jsonify(resultado), HTTP_BAD_REQUEST
    
    # GET: Listar estudiantes del profesor usando repository
    from repositories.session_repository import SessionRepository
    
    session_repo = SessionRepository()
    mis_estudiantes = []
    
    for estudiante in current_user.estudiantes:
        # Obtener estadísticas usando repository
        stats = session_repo.get_estadisticas_estudiante(
            estudiante_id=estudiante.id,
            profesor_id=current_user.id
        )
        
        mis_estudiantes.append({
            'id': estudiante.id,
            'nombre': estudiante.nombre,
            'codigo': estudiante.codigo,
            'email': estudiante.email,
            'total_sesiones': stats.get('total_sesiones', 0)
        })
    
    return jsonify(mis_estudiantes), HTTP_OK

# API para registro manual de sesiones (para profesores)
@app.route('/api/session/manual', methods=['POST'])
@login_required
def register_session_manual():
    """Endpoint para que profesores registren sesiones manualmente usando SessionService"""
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False, 
            'message': 'Solo profesores pueden registrar sesiones manualmente'
        }), HTTP_FORBIDDEN
    
    data = request.json
    
    # Debug: Ver qué datos llegan
    print("DEBUG - Datos recibidos en /api/session/manual:", data)
    
    # El frontend puede enviar 'estudiante_id' (number) o 'codigo_estudiante' (string)
    estudiante_id = data.get('estudiante_id')
    estudiante_codigo = data.get('codigo_estudiante') or data.get('estudiante_codigo') or data.get('codigo')
    
    # Si viene ID, buscar el estudiante y obtener su código
    if estudiante_id and not estudiante_codigo:
        estudiante = Estudiante.query.get(estudiante_id)
        if not estudiante:
            return jsonify({
                'success': False,
                'message': f'Estudiante con ID {estudiante_id} no encontrado'
            }), HTTP_BAD_REQUEST
        estudiante_codigo = estudiante.codigo
    
    if not estudiante_codigo:
        return jsonify({
            'success': False,
            'message': 'El código o ID del estudiante es requerido'
        }), HTTP_BAD_REQUEST
    
    # Validar campos requeridos
    maqueta = data.get('maqueta')
    puntaje = data.get('puntaje')
    tiempo_segundos = data.get('tiempo_segundos')
    
    if not all([maqueta, puntaje is not None, tiempo_segundos is not None]):
        return jsonify({
            'success': False,
            'message': 'Todos los campos son requeridos: maqueta, puntaje, tiempo_segundos'
        }), HTTP_BAD_REQUEST
    
    session_service = SessionService()
    
    # Crear sesión usando el servicio
    resultado = session_service.create_session(
        estudiante_codigo=estudiante_codigo,
        maqueta=maqueta,
        puntaje=float(puntaje),
        tiempo_segundos=int(tiempo_segundos),
        interacciones_ia=int(data.get('interacciones_ia', 0)),
        profesor_id=current_user.id,
        respuestas=data.get('respuestas', [])
    )
    
    if resultado['success']:
        return jsonify(resultado), HTTP_CREATED
    else:
        return jsonify(resultado), HTTP_BAD_REQUEST

# API para listar profesores (para estudiantes que se registran)
@app.route('/api/profesores', methods=['GET'])
def listar_profesores():
    """Lista todos los profesores usando AuthService"""
    auth_service = AuthService()
    profesores = auth_service.get_profesores_disponibles()
    return jsonify(profesores), HTTP_OK

# API para obtener todas las sesiones del profesor (para filtro por maqueta)
@app.route('/api/sesiones-todas')
@login_required
def obtener_sesiones_todas():
    """Obtiene todas las sesiones usando SessionRepository"""
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False, 
            'message': 'Solo profesores pueden acceder'
        }), HTTP_FORBIDDEN
    
    from repositories.session_repository import SessionRepository
    
    session_repo = SessionRepository()
    sesiones = session_repo.get_by_profesor(current_user.id)
    
    sesiones_data = []
    for s in sesiones:
        sesiones_data.append({
            'id': s.id,
            'estudiante_nombre': s.estudiante.nombre,
            'estudiante_codigo': s.estudiante.codigo,
            'maqueta': s.maqueta,
            'puntaje': s.puntaje,
            'tiempo_segundos': s.tiempo_segundos,
            'interacciones_ia': s.interacciones_ia,
            'fecha': s.fecha.isoformat()
        })
    
    return jsonify({'sesiones': sesiones_data}), HTTP_OK

# ============================================
# APIs ESPECÍFICAS PARA ESTUDIANTES
# ============================================

@app.route('/api/estudiante/analytics', methods=['GET'])
@login_required
def estudiante_analytics():
    """Analytics personales para el estudiante usando AnalyticsService"""
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False, 
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    try:
        analytics_service = AnalyticsService()
        resultado = analytics_service.get_analytics_estudiante(current_user.id)
        
        # 🔍 DEBUG: Log de respuesta
        print(f"📊 DEBUG Analytics Estudiante ID={current_user.id}:")
        print(f"  - success: {resultado.get('success')}")
        print(f"  - total_sesiones: {resultado.get('total_sesiones')}")
        print(f"  - tiene estadisticas: {'estadisticas' in resultado}")
        print(f"  - tiene por_maqueta: {'por_maqueta' in resultado}")
        print(f"  - tiene progreso_temporal: {'progreso_temporal' in resultado}")
        if resultado.get('por_maqueta'):
            print(f"  - por_maqueta[0]: {resultado['por_maqueta'][0]}")
        
        return jsonify(resultado), HTTP_OK
            
    except Exception as e:
        import traceback
        print("❌ Error en analytics estudiante:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'success': True,
            'total_sesiones': 0,
            'estadisticas': {
                'puntaje_promedio': 0,
                'puntaje_maximo': 0,
                'puntaje_minimo': 0,
                'tiempo_promedio_minutos': 0
            },
            'progreso_temporal': [],
            'por_maqueta': [],
            'insights': [f'Error al cargar analytics: {str(e)}']
        }), HTTP_OK

@app.route('/api/estudiante/analytics-profesor/<int:profesor_id>', methods=['GET'])
@login_required
def estudiante_analytics_por_profesor(profesor_id):
    """Analytics del estudiante filtrados por un profesor usando AnalyticsService"""
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False, 
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    # Verificar que el estudiante esté inscrito con este profesor
    profesor = Profesor.query.get(profesor_id)
    if not profesor:
        return jsonify({
            'success': False, 
            'message': 'Profesor no encontrado'
        }), HTTP_NOT_FOUND
    
    if current_user not in profesor.estudiantes:
        return jsonify({
            'success': False, 
            'message': 'No estás inscrito con este profesor'
        }), HTTP_FORBIDDEN
    
    try:
        analytics_service = AnalyticsService()
        resultado = analytics_service.get_analytics_estudiante_por_profesor(
            current_user.id, 
            profesor_id
        )
        
        # 🔍 DEBUG
        print(f"📊 Analytics por profesor - Estudiante ID={current_user.id}, Profesor ID={profesor_id}:")
        print(f"  - success: {resultado.get('success')}")
        print(f"  - total_sesiones: {resultado.get('total_sesiones')}")
        
        return jsonify(resultado), HTTP_OK
        
    except Exception as e:
        import traceback
        print(f"❌ Error en analytics estudiante por profesor (ID={profesor_id}):", str(e))
        print(traceback.format_exc())
        return jsonify({
            'success': True,  # ✅ Cambiar a True para no romper el frontend
            'profesor': {
                'id': profesor_id,
                'nombre': profesor.nombre if profesor else 'Desconocido'
            },
            'total_sesiones': 0,
            'estadisticas': {
                'puntaje_promedio': 0,
                'puntaje_maximo': 0,
                'puntaje_minimo': 0,
                'tiempo_promedio_minutos': 0
            },
            'por_maqueta': [],
            'progreso_temporal': [],
            'insights': [f'Error al cargar analytics: {str(e)}'],
            'sesiones': []
        }), HTTP_OK

@app.route('/api/estudiante/inscribirse', methods=['POST'])
@login_required
def estudiante_inscribirse():
    """Permite al estudiante inscribirse con un profesor usando AuthService"""
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False, 
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    data = request.json
    profesor_id = data.get('profesor_id')
    
    if not profesor_id:
        return jsonify({
            'success': False, 
            'message': 'ID de profesor requerido'
        }), HTTP_BAD_REQUEST
    
    auth_service = AuthService()
    
    # Usar método de AuthService para inscripción
    resultado = auth_service.inscribir_estudiante_profesor(
        estudiante_id=current_user.id,
        profesor_id=profesor_id
    )
    
    if resultado['success']:
        return jsonify(resultado), HTTP_CREATED
    else:
        status_code = HTTP_BAD_REQUEST if not resultado.get('ya_inscrito') else HTTP_BAD_REQUEST
        return jsonify(resultado), status_code

@app.route('/api/estudiante/profesores', methods=['GET'])
@login_required
def estudiante_profesores():
    """Lista de profesores usando repositories"""
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False, 
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    from repositories.session_repository import SessionRepository
    
    session_repo = SessionRepository()
    
    # Profesores con los que está inscrito
    mis_profesores = []
    for profesor in current_user.profesores:
        # Contar sesiones usando repository
        stats = session_repo.get_estadisticas_estudiante(
            current_user.id, 
            profesor.id
        )
        
        mis_profesores.append({
            'id': profesor.id,
            'nombre': profesor.nombre,
            'email': profesor.email,
            'institucion': profesor.institucion,
            'total_sesiones': stats.get('total_sesiones', 0),
            'inscrito': True
        })
    
    # Todos los profesores disponibles
    todos_profesores = Profesor.query.all()
    profesores_ids_inscritos = {p.id for p in current_user.profesores}
    
    profesores_disponibles = []
    for p in todos_profesores:
        profesores_disponibles.append({
            'id': p.id,
            'nombre': p.nombre,
            'email': p.email,
            'institucion': p.institucion,
            'inscrito': p.id in profesores_ids_inscritos
        })
    
    return jsonify({
        'success': True,
        'mis_profesores': mis_profesores,
        'total_profesores_inscritos': len(mis_profesores),
        'profesores_disponibles': profesores_disponibles
    }), HTTP_OK

# API para Unity - Registro de sesiones
@app.route('/api/unity/session', methods=['POST'])
def register_session():
    """Endpoint para que Unity envíe los datos de las sesiones usando SessionService"""
    data = request.json
    
    session_service = SessionService()
    
    # Crear sesión desde Unity (sin profesor_id)
    resultado = session_service.create_session(
        estudiante_codigo=data.get('codigo_estudiante'),
        maqueta=data.get('maqueta'),
        puntaje=data.get('puntaje'),
        tiempo_segundos=data.get('tiempo_segundos'),
        interacciones_ia=data.get('interacciones_ia', 0),
        profesor_id=None,  # Sesiones de Unity no tienen profesor asignado
        respuestas=data.get('respuestas', [])
    )
    
    if resultado['success']:
        return jsonify(resultado), HTTP_CREATED
    else:
        return jsonify(resultado), HTTP_BAD_REQUEST if 'no encontrado' in resultado.get('message', '').lower() else HTTP_BAD_REQUEST

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
