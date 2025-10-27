"""
🎮 Unity Routes - Blueprint de Integración Unity VR
===================================================

Endpoints API para Unity VR:
- POST /api/unity/session - Crear sesión desde Unity
- GET /api/unity/verify - Verificar conectividad

Patrón: RESTful API con validación y Service Layer
"""

from flask import Blueprint, jsonify, request
import time

from services.session_service import SessionService
from utils.constants import HTTP_OK, HTTP_CREATED, HTTP_BAD_REQUEST
from utils.logger import get_logger
from utils.validators import validate_puntaje

# Crear blueprint
unity_bp = Blueprint('unity', __name__)
logger = get_logger(__name__)


@unity_bp.route('/session', methods=['POST'])
def create_unity_session():
    """
    Crea una sesión VR desde Unity.
    
    POST /api/unity/session
    Body:
        {
            "codigo_estudiante": str,
            "maqueta": str,
            "puntaje": float (0-7),
            "tiempo_segundos": int,
            "interacciones_ia": int (opcional),
            "respuestas": array (opcional)
        }
    
    Returns:
        201 Created: Sesión creada exitosamente
        400 Bad Request: Datos inválidos
    
    Example:
        ```json
        {
            "codigo_estudiante": "JPEREZ",
            "maqueta": "Estructura Atómica",
            "puntaje": 6.5,
            "tiempo_segundos": 180,
            "interacciones_ia": 5,
            "respuestas": [
                {"pregunta": "¿Qué es un átomo?", "respuesta": "...", "correcta": true}
            ]
        }
        ```
    """
    inicio = time.time()
    
    try:
        data = request.json
        
        # Log de datos recibidos
        logger.info(f"Unity Session - Estudiante: {data.get('codigo_estudiante')}, Maqueta: {data.get('maqueta')}")
        logger.debug(f"Unity Session - Datos completos: {data}")
        
        # Validaciones básicas
        codigo_estudiante = data.get('codigo_estudiante')
        maqueta = data.get('maqueta')
        puntaje = data.get('puntaje')
        tiempo_segundos = data.get('tiempo_segundos')
        
        if not all([codigo_estudiante, maqueta, puntaje is not None, tiempo_segundos is not None]):
            logger.warning("Unity Session - Campos requeridos faltantes")
            return jsonify({
                'success': False,
                'message': 'Campos requeridos: codigo_estudiante, maqueta, puntaje, tiempo_segundos'
            }), HTTP_BAD_REQUEST
        
        # Validar puntaje
        try:
            puntaje_float = float(puntaje)
            if not validate_puntaje(puntaje_float):
                return jsonify({
                    'success': False,
                    'message': 'El puntaje debe estar entre 0 y 7'
                }), HTTP_BAD_REQUEST
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': 'Puntaje inválido'
            }), HTTP_BAD_REQUEST
        
        # Validar tiempo
        try:
            tiempo_int = int(tiempo_segundos)
            if tiempo_int < 0:
                return jsonify({
                    'success': False,
                    'message': 'El tiempo debe ser mayor a 0'
                }), HTTP_BAD_REQUEST
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': 'Tiempo inválido'
            }), HTTP_BAD_REQUEST
        
        # Crear sesión usando SessionService
        session_service = SessionService()
        
        resultado = session_service.create_session(
            estudiante_codigo=codigo_estudiante,
            maqueta=maqueta,
            puntaje=puntaje_float,
            tiempo_segundos=tiempo_int,
            interacciones_ia=int(data.get('interacciones_ia', 0)),
            profesor_id=None,  # Unity no especifica profesor
            respuestas=data.get('respuestas', [])
        )
        
        duracion = time.time() - inicio
        
        if resultado['success']:
            logger.info(f"Unity Session creada exitosamente en {duracion:.2f}s - ID={resultado['session_id']}")
            return jsonify(resultado), HTTP_CREATED
        else:
            logger.warning(f"Unity Session falló en {duracion:.2f}s: {resultado['message']}")
            return jsonify(resultado), HTTP_BAD_REQUEST
    
    except Exception as e:
        import traceback
        duracion = time.time() - inicio
        logger.error(f"Error en Unity Session ({duracion:.2f}s): {str(e)}")
        logger.debug(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'message': f'Error al crear sesión: {str(e)}'
        }), HTTP_BAD_REQUEST


@unity_bp.route('/verify', methods=['GET'])
def verify_connection():
    """
    Verifica la conectividad con el servidor.
    
    GET /api/unity/verify
    
    Returns:
        200 OK: Servidor disponible
    
    Example Response:
        ```json
        {
            "success": true,
            "message": "Servidor VR Analytics conectado",
            "version": "1.0.0",
            "timestamp": "2024-01-15T10:30:00"
        }
        ```
    """
    from datetime import datetime
    
    return jsonify({
        'success': True,
        'message': 'Servidor VR Analytics conectado',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'create_session': '/api/unity/session (POST)',
            'verify': '/api/unity/verify (GET)'
        }
    }), HTTP_OK
