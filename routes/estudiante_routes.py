"""
🎓 Estudiante Routes - Blueprint de API Estudiantes
===================================================

Endpoints API para estudiantes:
- GET /api/estudiante/analytics - Analytics personales
- GET /api/estudiante/analytics-profesor/<id> - Analytics filtrados por profesor
- POST /api/estudiante/inscribirse - Inscribirse con un profesor
- GET /api/estudiante/profesores - Lista de profesores disponibles

Patrón: RESTful API con Service Layer
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import time
from sqlalchemy import func

from models import db, Profesor, Estudiante, Sesion
from services.analytics_service import AnalyticsService
from services.auth_service import AuthService
from utils.constants import (
    HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST, HTTP_FORBIDDEN, HTTP_NOT_FOUND
)
from utils.logger import get_logger

# Crear blueprint
estudiante_bp = Blueprint('estudiante', __name__)
logger = get_logger(__name__)


@estudiante_bp.route('/analytics', methods=['GET'])
@login_required
def estudiante_analytics():
    """
    Analytics personales del estudiante.
    
    GET /api/estudiante/analytics
    
    Returns:
        200 OK: Estadísticas personales
        403 Forbidden: Si no es estudiante
    """
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False,
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    try:
        analytics_service = AnalyticsService()
        resultado = analytics_service.get_analytics_estudiante(current_user.id)
        
        logger.debug(f"Analytics Estudiante ID={current_user.id}: {resultado.get('total_sesiones')} sesiones")
        
        return jsonify(resultado), HTTP_OK
            
    except Exception as e:
        import traceback
        logger.error(f"Error en analytics estudiante: {str(e)}")
        logger.debug(traceback.format_exc())
        
        return jsonify({
            'success': True,
            'total_sesiones': 0,
            'estadisticas': {
                'puntaje_promedio': 0,
                'puntaje_maximo': 0,
                'puntaje_minimo': 0,
                'tiempo_promedio_segundos': 0
            },
            'progreso_temporal': [],
            'por_maqueta': [],
            'insights': [f'Error al cargar analytics: {str(e)}']
        }), HTTP_OK


@estudiante_bp.route('/analytics-profesor/<int:profesor_id>', methods=['GET'])
@login_required
def estudiante_analytics_por_profesor(profesor_id):
    """
    Analytics del estudiante filtrados por un profesor específico.
    
    GET /api/estudiante/analytics-profesor/<profesor_id>
    
    Returns:
        200 OK: Estadísticas filtradas por profesor
        403 Forbidden: Si no es estudiante o no está inscrito
        404 Not Found: Si el profesor no existe
    """
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False,
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    # Verificar profesor
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
        
        logger.debug(f"Analytics por profesor - Estudiante={current_user.id}, Profesor={profesor_id}")
        
        return jsonify(resultado), HTTP_OK
        
    except Exception as e:
        import traceback
        logger.error(f"Error en analytics por profesor: {str(e)}")
        logger.debug(traceback.format_exc())
        
        return jsonify({
            'success': True,
            'profesor': {
                'id': profesor_id,
                'nombre': profesor.nombre if profesor else 'Desconocido'
            },
            'total_sesiones': 0,
            'estadisticas': {
                'puntaje_promedio': 0,
                'puntaje_maximo': 0,
                'puntaje_minimo': 0,
                'tiempo_promedio_segundos': 0
            },
            'por_maqueta': [],
            'progreso_temporal': [],
            'insights': [f'Error al cargar analytics: {str(e)}'],
            'sesiones': []
        }), HTTP_OK


@estudiante_bp.route('/inscribirse', methods=['POST'])
@login_required
def estudiante_inscribirse():
    """
    Inscribe al estudiante con un profesor.
    
    POST /api/estudiante/inscribirse
    Body:
        {
            "profesor_id": int
        }
    
    Returns:
        201 Created: Inscripción exitosa
        400 Bad Request: Datos inválidos o ya inscrito
        403 Forbidden: Si no es estudiante
    """
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
    
    resultado = auth_service.inscribir_estudiante_profesor(
        estudiante_id=current_user.id,
        profesor_id=profesor_id
    )
    
    return jsonify(resultado), HTTP_CREATED if resultado['success'] else HTTP_BAD_REQUEST


@estudiante_bp.route('/profesores', methods=['GET'])
@login_required
def estudiante_profesores():
    """
    Lista de profesores con estadísticas del estudiante.
    
    GET /api/estudiante/profesores
    
    Returns:
        200 OK: Array de profesores con stats
        403 Forbidden: Si no es estudiante
    """
    inicio = time.time()
    logger.info(f"Profesores - Estudiante ID={current_user.id}")
    
    if not isinstance(current_user, Estudiante):
        return jsonify({
            'success': False,
            'message': 'Solo para estudiantes'
        }), HTTP_FORBIDDEN
    
    # Query optimizada: obtener stats en bloque
    stats_query = db.session.query(
        Sesion.profesor_id,
        func.count(Sesion.id).label('total_sesiones'),
        func.avg(Sesion.puntaje).label('promedio_puntaje')
    ).filter(
        Sesion.estudiante_id == current_user.id
    ).group_by(Sesion.profesor_id).all()
    
    stats_dict = {
        row.profesor_id: {
            'total_sesiones': row.total_sesiones,
            'promedio_puntaje': round(row.promedio_puntaje, 2) if row.promedio_puntaje else 0
        }
        for row in stats_query
    }
    
    # Lista de profesores
    profesores_data = []
    for profesor in current_user.profesores:
        stats = stats_dict.get(profesor.id, {'total_sesiones': 0, 'promedio_puntaje': 0})
        
        profesores_data.append({
            'id': profesor.id,
            'nombre': profesor.nombre,
            'institucion': profesor.institucion,
            'email': profesor.email,
            'total_sesiones': stats['total_sesiones'],
            'promedio_puntaje': stats['promedio_puntaje']
        })
    
    duracion = time.time() - inicio
    logger.info(f"Profesores listados en {duracion:.2f}s ({len(profesores_data)} profesores)")
    
    return jsonify(profesores_data), HTTP_OK
