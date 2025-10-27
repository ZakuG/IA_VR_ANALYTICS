"""
🔌 API Routes - Blueprint de API REST (Profesor)
=================================================

Endpoints API para profesores:
- GET /api/analytics - Analytics completo
- GET/POST /api/estudiantes - Gestión de estudiantes
- POST /api/session/manual - Registro manual de sesiones
- GET /api/profesores - Listar profesores
- GET /api/sesiones-todas - Todas las sesiones
- GET /api/regresion-simple - Regresión lineal simple
- GET /api/regresion-multiple - Regresión lineal múltiple

Patrón: RESTful API con Service Layer
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import time
import numpy as np

from models import db, Profesor, Estudiante, Sesion
from services.analytics_service import AnalyticsService
from services.session_service import SessionService
from services.auth_service import AuthService
from repositories.session_repository import SessionRepository
from utils.constants import (
    HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST, HTTP_FORBIDDEN
)
from utils.logger import get_logger
from sqlalchemy import func

# Crear blueprint
api_bp = Blueprint('api', __name__)
logger = get_logger(__name__)


@api_bp.route('/analytics')
@login_required
def get_analytics():
    """
    Analytics completo para profesor.
    
    GET /api/analytics
    
    Returns:
        200 OK: Objeto JSON con estadísticas, gráficos, ML
        403 Forbidden: Si no es profesor
    """
    inicio = time.time()
    logger.info(f"Analytics - Profesor ID={current_user.id}")
    
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False,
            'message': 'Solo para profesores'
        }), HTTP_FORBIDDEN
    
    try:
        analytics_service = AnalyticsService()
        resultado = analytics_service.get_analytics_profesor(current_user.id)
        
        duracion = time.time() - inicio
        logger.info(f"Analytics completado en {duracion:.2f}s")
        
        return jsonify(resultado), HTTP_OK
            
    except Exception as e:
        import traceback
        duracion = time.time() - inicio
        logger.error(f"Error en analytics ({duracion:.2f}s): {str(e)}")
        logger.debug(traceback.format_exc())
        
        return jsonify({
            'error': str(e),
            'message': 'Error al procesar los datos',
            'estadisticas': {'general': {}},
            'por_maqueta': {},
            'ml_clasificacion': {'modelo_disponible': False}
        }), HTTP_OK


@api_bp.route('/estudiantes', methods=['GET', 'POST'])
@login_required
def estudiantes():
    """
    Gestión de estudiantes del profesor.
    
    GET /api/estudiantes - Lista estudiantes
    POST /api/estudiantes - Inscribe estudiante
    
    POST Body:
        {
            "codigo": str - Código del estudiante
        }
    
    Returns:
        200 OK: Lista de estudiantes
        201 Created: Estudiante inscrito
        400 Bad Request: Datos inválidos
        403 Forbidden: Si no es profesor
    """
    inicio = time.time()
    logger.info(f"Estudiantes - Profesor ID={current_user.id}")
    
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False,
            'message': 'Solo para profesores'
        }), HTTP_FORBIDDEN
    
    if request.method == 'POST':
        data = request.json
        auth_service = AuthService()
        
        resultado = auth_service.inscribir_estudiante_profesor(
            estudiante_codigo=data.get('codigo'),
            profesor_id=current_user.id
        )
        
        return jsonify(resultado), HTTP_CREATED if resultado['success'] else HTTP_BAD_REQUEST
    
    # GET: Listar estudiantes OPTIMIZADO
    stats_query = db.session.query(
        Sesion.estudiante_id,
        func.count(Sesion.id).label('total_sesiones'),
        func.avg(Sesion.puntaje).label('promedio_puntaje')
    ).filter(
        Sesion.profesor_id == current_user.id
    ).group_by(Sesion.estudiante_id).all()
    
    stats_dict = {
        row.estudiante_id: {
            'total_sesiones': row.total_sesiones,
            'promedio_puntaje': round(row.promedio_puntaje, 2) if row.promedio_puntaje else 0
        }
        for row in stats_query
    }
    
    mis_estudiantes = []
    for estudiante in current_user.estudiantes:
        stats = stats_dict.get(estudiante.id, {'total_sesiones': 0, 'promedio_puntaje': 0})
        
        mis_estudiantes.append({
            'id': estudiante.id,
            'nombre': estudiante.nombre,
            'codigo': estudiante.codigo,
            'email': estudiante.email,
            'total_sesiones': stats['total_sesiones'],
            'promedio_puntaje': stats['promedio_puntaje']
        })
    
    duracion = time.time() - inicio
    logger.info(f"Estudiantes listados en {duracion:.2f}s ({len(mis_estudiantes)} estudiantes)")
    
    return jsonify(mis_estudiantes), HTTP_OK


@api_bp.route('/session/manual', methods=['POST'])
@login_required
def register_session_manual():
    """
    Registro manual de sesión por profesor.
    
    POST /api/session/manual
    Body:
        {
            "estudiante_id": int | "codigo_estudiante": str,
            "maqueta": str,
            "puntaje": float,
            "tiempo_segundos": int,
            "interacciones_ia": int (opcional),
            "respuestas": array (opcional)
        }
    
    Returns:
        201 Created: Sesión creada
        400 Bad Request: Datos inválidos
        403 Forbidden: Si no es profesor
    """
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False,
            'message': 'Solo profesores pueden registrar sesiones manualmente'
        }), HTTP_FORBIDDEN
    
    data = request.json
    logger.debug(f"Registro manual - Datos: {data}")
    
    # Obtener código de estudiante
    estudiante_id = data.get('estudiante_id')
    estudiante_codigo = data.get('codigo_estudiante') or data.get('estudiante_codigo') or data.get('codigo')
    
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
    
    resultado = session_service.create_session(
        estudiante_codigo=estudiante_codigo,
        maqueta=maqueta,
        puntaje=float(puntaje),
        tiempo_segundos=int(tiempo_segundos),
        interacciones_ia=int(data.get('interacciones_ia', 0)),
        profesor_id=current_user.id,
        respuestas=data.get('respuestas', [])
    )
    
    return jsonify(resultado), HTTP_CREATED if resultado['success'] else HTTP_BAD_REQUEST


@api_bp.route('/profesores', methods=['GET'])
def listar_profesores():
    """
    Lista todos los profesores disponibles.
    
    GET /api/profesores
    
    Returns:
        200 OK: Array de profesores
    """
    auth_service = AuthService()
    profesores = auth_service.get_profesores_disponibles()
    return jsonify(profesores), HTTP_OK


@api_bp.route('/sesiones-todas')
@login_required
def obtener_sesiones_todas():
    """
    Obtiene todas las sesiones del profesor.
    
    GET /api/sesiones-todas
    
    Returns:
        200 OK: Array de sesiones
        403 Forbidden: Si no es profesor
    """
    inicio = time.time()
    logger.info(f"Sesiones todas - Profesor ID={current_user.id}")
    
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False,
            'message': 'Solo profesores pueden acceder'
        }), HTTP_FORBIDDEN
    
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
    
    duracion = time.time() - inicio
    logger.info(f"Sesiones listadas en {duracion:.2f}s ({len(sesiones_data)} sesiones)")
    
    return jsonify({'sesiones': sesiones_data}), HTTP_OK


@api_bp.route('/regresion-simple')
@login_required
def regresion_simple():
    """
    Regresión lineal simple: Tiempo → Puntaje.
    
    GET /api/regresion-simple
    
    Returns:
        200 OK: Modelo, fórmula, métricas, gráfico
        403 Forbidden: Si no es profesor
    """
    inicio = time.time()
    logger.info(f"Regresión simple - Profesor ID={current_user.id}")
    
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False,
            'message': 'Solo profesores pueden acceder'
        }), HTTP_FORBIDDEN
    
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_absolute_error
        
        session_repo = SessionRepository()
        sesiones = session_repo.get_by_profesor(current_user.id)
        
        if len(sesiones) < 5:
            return jsonify({
                'success': False,
                'message': 'Se necesitan al menos 5 sesiones para regresión'
            }), HTTP_OK
        
        # Preparar datos
        X = np.array([[s.tiempo_segundos] for s in sesiones])
        y = np.array([s.puntaje for s in sesiones])
        
        # Entrenar modelo
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # Métricas
        y_pred = modelo.predict(X)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        
        # Precisión
        if r2 > 0.7:
            precision = "Excelente"
        elif r2 > 0.4:
            precision = "Moderada"
        else:
            precision = "Baja"
        
        # Fórmula
        coef = modelo.coef_[0]
        intercept = modelo.intercept_
        formula = f"Puntaje = {intercept:.4f} + ({coef:.6f} × Tiempo_segundos)"
        
        # Interpretación
        if coef > 0:
            interpretacion = f"A mayor tiempo en VR, mayor puntaje. Por cada segundo adicional, el puntaje aumenta {coef:.4f} puntos."
        else:
            interpretacion = f"A mayor tiempo en VR, menor puntaje. Podría indicar dificultad o confusión."
        
        # Datos para gráfico
        X_plot = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_plot = modelo.predict(X_plot)
        
        # Formato compatible con dashboard-charts.js
        resultado = {
            'success': True,
            'r2_score': float(r2),
            'mae': float(mae),
            'precision': precision,
            'formula': formula,
            'interpretacion': interpretacion,
            'n_samples': len(sesiones),
            'coeficiente': float(coef),
            'intercepto': float(intercept),
            # Datos adicionales para gráficos
            'datos': {
                'X_real': X.flatten().tolist(),
                'y_real': y.tolist(),
                'X_linea': X_plot.flatten().tolist(),
                'y_linea': y_plot.tolist()
            }
        }
        
        duracion = time.time() - inicio
        logger.info(f"Regresión simple completada en {duracion:.2f}s (R²={r2:.4f})")
        
        return jsonify(resultado), HTTP_OK
    
    except Exception as e:
        logger.error(f"Error en regresión simple: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al calcular regresión: {str(e)}'
        }), HTTP_OK


@api_bp.route('/regresion-multiple')
@login_required
def regresion_multiple():
    """
    Regresión lineal múltiple: Tiempo + Interacciones IA → Puntaje.
    
    GET /api/regresion-multiple
    
    Returns:
        200 OK: Modelo, fórmula, métricas, importancia de features
        403 Forbidden: Si no es profesor
    """
    inicio = time.time()
    logger.info(f"Regresión múltiple - Profesor ID={current_user.id}")
    
    if not isinstance(current_user, Profesor):
        return jsonify({
            'success': False,
            'message': 'Solo profesores pueden acceder'
        }), HTTP_FORBIDDEN
    
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_absolute_error
        
        session_repo = SessionRepository()
        sesiones = session_repo.get_by_profesor(current_user.id)
        
        if len(sesiones) < 10:
            return jsonify({
                'success': False,
                'message': 'Se necesitan al menos 10 sesiones para regresión múltiple'
            }), HTTP_OK
        
        # Preparar datos
        X = np.array([[s.tiempo_segundos, s.interacciones_ia] for s in sesiones])
        y = np.array([s.puntaje for s in sesiones])
        
        # Entrenar modelo
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        # Métricas
        y_pred = modelo.predict(X)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        
        # Precisión
        if r2 > 0.7:
            precision = "Excelente"
        elif r2 > 0.4:
            precision = "Moderada"
        else:
            precision = "Baja"
        
        # Fórmula
        coef_tiempo = modelo.coef_[0]
        coef_ia = modelo.coef_[1]
        intercept = modelo.intercept_
        formula = f"Puntaje = {intercept:.4f} + ({coef_tiempo:.6f} × Tiempo) + ({coef_ia:.6f} × Interacciones_IA)"
        
        # Importancia de features
        importancia = [
            {'feature': 'Tiempo (segundos)', 'coeficiente': float(coef_tiempo)},
            {'feature': 'Interacciones IA', 'coeficiente': float(coef_ia)}
        ]
        
        # Interpretación
        interpretaciones = []
        if abs(coef_tiempo) > 0.001:
            interpretaciones.append(
                f"{'Mayor' if coef_tiempo > 0 else 'Menor'} tiempo correlaciona con {'mejor' if coef_tiempo > 0 else 'peor'} puntaje"
            )
        if abs(coef_ia) > 0.01:
            interpretaciones.append(
                f"{'Más' if coef_ia > 0 else 'Menos'} interacciones con IA correlaciona con {'mejor' if coef_ia > 0 else 'peor'} rendimiento"
            )
        interpretacion = ". ".join(interpretaciones) if interpretaciones else "Las variables tienen poco impacto en el modelo."
        
        # Formato compatible con dashboard-charts.js
        resultado = {
            'success': True,
            'r2_score': float(r2),
            'mae': float(mae),
            'precision': precision,
            'formula': formula,
            'interpretacion': interpretacion,
            'n_samples': len(sesiones),
            'n_features': 2,
            'coeficientes': importancia
        }
        
        duracion = time.time() - inicio
        logger.info(f"Regresión múltiple completada en {duracion:.2f}s (R²={r2:.4f})")
        
        return jsonify(resultado), HTTP_OK
    
    except Exception as e:
        logger.error(f"Error en regresión múltiple: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al calcular regresión: {str(e)}'
        }), HTTP_OK
