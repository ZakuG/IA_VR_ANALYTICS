"""
Session Repository - Gestión de sesiones VR
Maneja todas las operaciones CRUD de sesiones
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models import db, Sesion


class SessionRepository:
    """Repository para gestionar sesiones VR"""
    
    @staticmethod
    def create(estudiante_id: int, maqueta: str, puntaje: float, 
               tiempo_segundos: int, interacciones_ia: int, 
               profesor_id: Optional[int] = None) -> Sesion:
        """
        Crea una nueva sesión
        
        Args:
            estudiante_id: ID del estudiante
            maqueta: Nombre de la maqueta VR
            puntaje: Puntaje obtenido (0-7)
            tiempo_segundos: Tiempo en segundos
            interacciones_ia: Número de interacciones con IA
            profesor_id: ID del profesor que evalúa (opcional)
            
        Returns:
            Sesion: La sesión creada
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not 0 <= puntaje <= 7:
            raise ValueError("El puntaje debe estar entre 0 y 7")
        
        if tiempo_segundos < 0:
            raise ValueError("El tiempo no puede ser negativo")
        
        if interacciones_ia < 0:
            raise ValueError("Las interacciones no pueden ser negativas")
        
        sesion = Sesion(
            estudiante_id=estudiante_id,
            maqueta=maqueta,
            puntaje=puntaje,
            tiempo_segundos=tiempo_segundos,
            interacciones_ia=interacciones_ia,
            profesor_id=profesor_id,
            fecha=datetime.utcnow()
        )
        
        db.session.add(sesion)
        db.session.commit()
        
        return sesion
    
    @staticmethod
    def get_by_id(sesion_id: int) -> Optional[Sesion]:
        """
        Obtiene una sesión por ID
        
        Args:
            sesion_id: ID de la sesión
            
        Returns:
            Sesion o None si no existe
        """
        return Sesion.query.get(sesion_id)
    
    @staticmethod
    def get_by_estudiante(estudiante_id: int) -> List[Sesion]:
        """
        Obtiene todas las sesiones de un estudiante CON EAGER LOADING
        Optimizado para evitar N+1 queries
        
        Args:
            estudiante_id: ID del estudiante
            
        Returns:
            Lista de sesiones con relaciones pre-cargadas
        """
        return Sesion.query\
                    .filter_by(estudiante_id=estudiante_id)\
                    .options(joinedload(Sesion.estudiante))\
                    .order_by(Sesion.fecha.desc())\
                    .all()
    
    @staticmethod
    def get_by_profesor(profesor_id: int) -> List[Sesion]:
        """
        Obtiene todas las sesiones evaluadas por un profesor CON EAGER LOADING
        Optimizado para evitar N+1 queries
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            Lista de sesiones con estudiante pre-cargado
        """
        return Sesion.query\
                    .filter_by(profesor_id=profesor_id)\
                    .options(joinedload(Sesion.estudiante))\
                    .order_by(Sesion.fecha.desc())\
                    .all()
    
    @staticmethod
    def count_by_profesor(profesor_id: int) -> int:
        """
        Cuenta rápidamente las sesiones de un profesor (para cache)
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            Número de sesiones
        """
        return Sesion.query.filter_by(profesor_id=profesor_id).count()
    
    @staticmethod
    def count_by_estudiante(estudiante_id: int) -> int:
        """
        Cuenta rápidamente las sesiones de un estudiante (para cache)
        
        Args:
            estudiante_id: ID del estudiante
            
        Returns:
            Número de sesiones
        """
        return Sesion.query.filter_by(estudiante_id=estudiante_id).count()
    
    @staticmethod
    def get_by_maqueta(maqueta: str, profesor_id: Optional[int] = None) -> List[Sesion]:
        """
        Obtiene sesiones por maqueta, opcionalmente filtradas por profesor
        
        Args:
            maqueta: Nombre de la maqueta
            profesor_id: ID del profesor (opcional)
            
        Returns:
            Lista de sesiones
        """
        query = Sesion.query.filter_by(maqueta=maqueta)
        
        if profesor_id:
            query = query.filter_by(profesor_id=profesor_id)
        
        return query.order_by(Sesion.fecha.desc()).all()
    
    @staticmethod
    def get_all() -> List[Sesion]:
        """
        Obtiene todas las sesiones
        
        Returns:
            Lista de todas las sesiones
        """
        return Sesion.query.order_by(Sesion.fecha.desc()).all()
    
    @staticmethod
    def get_estadisticas_profesor(profesor_id: int) -> Dict[str, Any]:
        """
        Calcula estadísticas de sesiones de un profesor
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            Diccionario con estadísticas
        """
        sesiones = SessionRepository.get_by_profesor(profesor_id)
        
        if not sesiones:
            return {
                'total_sesiones': 0,
                'total_estudiantes': 0,
                'promedio_puntaje': 0,
                'promedio_tiempo': 0
            }
        
        estudiantes_unicos = len(set(s.estudiante_id for s in sesiones))
        promedio_puntaje = sum(s.puntaje for s in sesiones) / len(sesiones)
        promedio_tiempo = sum(s.tiempo_segundos for s in sesiones) / len(sesiones) / 60
        
        return {
            'total_sesiones': len(sesiones),
            'total_estudiantes': estudiantes_unicos,
            'promedio_puntaje': round(promedio_puntaje, 2),
            'promedio_tiempo': round(promedio_tiempo, 2)
        }
    
    @staticmethod
    def delete(sesion_id: int) -> bool:
        """
        Elimina una sesión
        
        Args:
            sesion_id: ID de la sesión
            
        Returns:
            True si se eliminó, False si no existía
        """
        sesion = SessionRepository.get_by_id(sesion_id)
        
        if not sesion:
            return False
        
        db.session.delete(sesion)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_maquetas_unicas(profesor_id: Optional[int] = None) -> List[str]:
        """
        Obtiene lista de maquetas únicas
        
        Args:
            profesor_id: Filtrar por profesor (opcional)
            
        Returns:
            Lista de nombres de maquetas
        """
        query = db.session.query(Sesion.maqueta).distinct()
        
        if profesor_id:
            query = query.filter(Sesion.profesor_id == profesor_id)
        
        return [m[0] for m in query.all()]
    
    @staticmethod
    def get_estadisticas_estudiante(estudiante_id: int, profesor_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un estudiante específico
        
        Args:
            estudiante_id: ID del estudiante
            profesor_id: ID del profesor (opcional, para filtrar)
            
        Returns:
            Dict con estadísticas del estudiante
        """
        if profesor_id:
            sesiones = Sesion.query.filter_by(
                estudiante_id=estudiante_id,
                profesor_id=profesor_id
            ).all()
        else:
            sesiones = SessionRepository.get_by_estudiante(estudiante_id)
        
        if not sesiones:
            return {
                'total_sesiones': 0,
                'promedio_puntaje': 0,
                'promedio_tiempo': 0,
                'mejor_puntaje': 0,
                'peor_puntaje': 0
            }
        
        puntajes = [s.puntaje for s in sesiones]
        tiempos = [s.tiempo_segundos for s in sesiones]
        
        return {
            'total_sesiones': len(sesiones),
            'promedio_puntaje': round(sum(puntajes) / len(puntajes), 2),
            'promedio_tiempo': round(sum(tiempos) / len(tiempos), 2),
            'mejor_puntaje': max(puntajes),
            'peor_puntaje': min(puntajes)
        }

