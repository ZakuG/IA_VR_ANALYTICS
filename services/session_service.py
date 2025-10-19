"""
Session Service - Servicio de gestión de sesiones
Lógica de negocio para sesiones VR
"""

from typing import Dict, List, Any, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.session_repository import SessionRepository
from repositories.estudiante_repository import EstudianteRepository
from repositories.profesor_repository import ProfesorRepository


class SessionService:
    """Servicio para gestionar sesiones VR"""
    
    def __init__(self):
        """Inicializa el servicio de sesiones"""
        self.session_repo = SessionRepository()
        self.estudiante_repo = EstudianteRepository()
        self.profesor_repo = ProfesorRepository()
    
    def create_session(self, estudiante_codigo: str, maqueta: str, 
                      puntaje: float, tiempo_segundos: int, 
                      interacciones_ia: int, 
                      profesor_email: Optional[str] = None,
                      profesor_id: Optional[int] = None,
                      respuestas: Optional[List] = None) -> Dict[str, Any]:
        """
        Crea una nueva sesión VR
        
        Args:
            estudiante_codigo: Código del estudiante
            maqueta: Nombre de la maqueta
            puntaje: Puntaje obtenido (0-7)
            tiempo_segundos: Tiempo en segundos
            interacciones_ia: Interacciones con IA
            profesor_email: Email del profesor (opcional)
            profesor_id: ID del profesor (opcional, alternativa a profesor_email)
            respuestas: Lista de respuestas del estudiante (opcional)
            
        Returns:
            Diccionario con resultado de la operación
        """
        # Validar estudiante
        estudiante = self.estudiante_repo.get_by_codigo(estudiante_codigo)
        if not estudiante:
            return {
                'success': False,
                'message': f'Estudiante con código {estudiante_codigo} no encontrado'
            }
        
        # Validar profesor (opcional - puede venir por email o por id)
        final_profesor_id = None
        
        if profesor_id:
            # Si se proporciona profesor_id directamente, usarlo
            profesor = self.profesor_repo.get_by_id(profesor_id)
            if not profesor:
                return {
                    'success': False,
                    'message': f'Profesor con ID {profesor_id} no encontrado'
                }
            final_profesor_id = profesor.id
            
        elif profesor_email:
            # Si se proporciona email, buscar por email
            profesor = self.profesor_repo.get_by_email(profesor_email)
            if not profesor:
                return {
                    'success': False,
                    'message': f'Profesor con email {profesor_email} no encontrado'
                }
            final_profesor_id = profesor.id
        
        try:
            # Crear sesión
            sesion = self.session_repo.create(
                estudiante_id=estudiante.id,
                maqueta=maqueta,
                puntaje=puntaje,
                tiempo_segundos=tiempo_segundos,
                interacciones_ia=interacciones_ia,
                profesor_id=final_profesor_id
            )
            
            # Si hay respuestas, guardarlas
            if respuestas:
                sesion.set_respuestas(respuestas)
                from models import db
                db.session.commit()
            
            return {
                'success': True,
                'message': 'Sesión registrada correctamente',
                'sesion_id': sesion.id,
                'estudiante': estudiante.nombre,
                'puntaje': sesion.puntaje
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al crear sesión: {str(e)}'
            }
    
    def get_sesiones_profesor(self, profesor_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las sesiones de un profesor con información detallada
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            Lista de sesiones serializadas
        """
        sesiones = self.session_repo.get_by_profesor(profesor_id)
        
        return [{
            'id': s.id,
            'estudiante_nombre': s.estudiante.nombre,
            'estudiante_codigo': s.estudiante.codigo,
            'maqueta': s.maqueta,
            'puntaje': s.puntaje,
            'tiempo_segundos': s.tiempo_segundos,
            'interacciones_ia': s.interacciones_ia,
            'fecha': s.fecha.isoformat()
        } for s in sesiones]
    
    def get_maquetas_disponibles(self, profesor_id: Optional[int] = None) -> List[str]:
        """
        Obtiene lista de maquetas disponibles
        
        Args:
            profesor_id: Filtrar por profesor (opcional)
            
        Returns:
            Lista de nombres de maquetas
        """
        return self.session_repo.get_maquetas_unicas(profesor_id)
    
    def validar_datos_sesion(self, puntaje: float, tiempo_segundos: int, 
                            interacciones_ia: int) -> Dict[str, Any]:
        """
        Valida los datos de una sesión antes de crearla
        
        Args:
            puntaje: Puntaje a validar
            tiempo_segundos: Tiempo a validar
            interacciones_ia: Interacciones a validar
            
        Returns:
            Diccionario con resultado de validación
        """
        errores = []
        
        if not 0 <= puntaje <= 7:
            errores.append("El puntaje debe estar entre 0 y 7")
        
        if tiempo_segundos < 0:
            errores.append("El tiempo no puede ser negativo")
        
        if tiempo_segundos > 7200:  # 2 horas
            errores.append("El tiempo es demasiado largo (máximo 2 horas)")
        
        if interacciones_ia < 0:
            errores.append("Las interacciones no pueden ser negativas")
        
        if interacciones_ia > 1000:
            errores.append("Número de interacciones inusualmente alto")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores
        }
