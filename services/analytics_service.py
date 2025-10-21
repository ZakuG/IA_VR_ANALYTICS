"""
Analytics Service - Servicio de análisis de datos
Encapsula toda la lógica de análisis y ML
"""

from typing import Dict, List, Any, Optional
from functools import wraps
import time
import sys
import os
import pandas as pd

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.session_repository import SessionRepository
from data_analytics import AnalizadorAvanzado


# ========== CACHE SIMPLE ==========
_cache = {}

def cache_result(ttl_seconds: int = 300):
    """Decorador para cachear resultados (5 min por defecto)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            
            if cache_key in _cache:
                result, timestamp = _cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator


class AnalyticsService:
    """Servicio para análisis de datos y ML"""
    
    def __init__(self):
        """Inicializa el servicio de analytics"""
        self.session_repo = SessionRepository()
    
    @cache_result(ttl_seconds=300)  # Cache de 5 minutos
    def get_analytics_profesor(self, profesor_id: int) -> Dict[str, Any]:
        """
        Obtiene análisis completo para un profesor
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            Diccionario con todos los análisis
        """
        # Obtener sesiones del profesor
        sesiones = self.session_repo.get_by_profesor(profesor_id)
        
        if not sesiones:
            return self._empty_analytics_response()
        
        # Crear analizador directamente con objetos Sesion (no convertir a dict)
        analizador = AnalizadorAvanzado(sesiones)
        
        # Generar análisis
        return {
            'success': True,
            'total_sesiones': len(sesiones),
            'estadisticas': analizador.estadisticas_descriptivas(),
            'visualizacion': analizador.datos_para_visualizacion(),
            'clustering': analizador.clustering_estudiantes(),
            'prediccion': analizador.prediccion_rendimiento(),
            'correlaciones': analizador.correlaciones_avanzadas(),
            'estudiantes_riesgo': analizador.estudiantes_en_riesgo(),
            'ranking': analizador.ranking_estudiantes(),
            'insights': analizador.generar_insights(),
            'por_maqueta': analizador.analisis_por_maqueta(),
            'ml_clasificacion': analizador.clasificacion_binaria_aprobacion(),
            'ml_clustering': analizador.kmeans_clustering_profesional(),
            'ml_correlaciones': analizador.correlaciones_con_pvalues()
        }
    
    def get_analytics_estudiante(self, estudiante_id: int) -> Dict[str, Any]:
        """
        Obtiene análisis para un estudiante
        
        Args:
            estudiante_id: ID del estudiante
            
        Returns:
            Diccionario con análisis del estudiante
        """
        sesiones = self.session_repo.get_by_estudiante(estudiante_id)
        
        if not sesiones:
            return {
                'success': True,  # ✅ Cambiar a True para que el frontend no falle
                'total_sesiones': 0,
                'estadisticas': {
                    'puntaje_promedio': 0,
                    'puntaje_maximo': 0,
                    'puntaje_minimo': 0,
                    'tiempo_promedio_minutos': 0
                },
                'por_maqueta': [],
                'progreso_temporal': [],
                'insights': ['No tienes sesiones registradas aún. ¡Comienza a practicar!'],
                'sesiones': []
            }
        
        # Calcular estadísticas base (lógica extraída)
        estadisticas_base = self._calcular_estadisticas_base(sesiones)
        
        return {
            'success': True,
            'total_sesiones': estadisticas_base['total_sesiones'],
            'estadisticas': estadisticas_base['estadisticas'],
            'por_maqueta': estadisticas_base['por_maqueta'],
            'progreso_temporal': estadisticas_base['progreso_temporal'],
            'insights': self._generar_insights_estudiante(sesiones),
            'sesiones': self._serializar_sesiones(sesiones)
        }
    
    def get_analytics_por_maqueta(self, profesor_id: int, maqueta: str) -> Dict[str, Any]:
        """
        Obtiene análisis de una maqueta específica
        
        Args:
            profesor_id: ID del profesor
            maqueta: Nombre de la maqueta
            
        Returns:
            Análisis de la maqueta
        """
        sesiones = self.session_repo.get_by_maqueta(maqueta, profesor_id)
        
        if not sesiones:
            return {
                'success': False,
                'message': 'No hay datos para esta maqueta'
            }
        
        # Pasar sesiones directamente, no como diccionarios
        analizador = AnalizadorAvanzado(sesiones)
        
        return {
            'success': True,
            'maqueta': maqueta,
            'total_sesiones': len(sesiones),
            'estadisticas': analizador.estadisticas_descriptivas(),
            'estudiantes': len(set(s.estudiante_id for s in sesiones)),
            'visualizacion': analizador.datos_para_visualizacion()
        }
    
    # Métodos privados helpers
    
    def _calcular_estadisticas_base(self, sesiones: List) -> Dict[str, Any]:
        """
        Calcula estadísticas base comunes para análisis de estudiante.
        
        REFACTORIZACIÓN Issue #3: Extrae lógica duplicada de get_analytics_estudiante()
        y get_analytics_estudiante_por_profesor() para eliminar ~50 líneas de duplicación.
        
        Args:
            sesiones: Lista de objetos Sesion
            
        Returns:
            Dict con estadísticas base:
                - total_sesiones
                - estadisticas (puntaje_promedio, puntaje_maximo, puntaje_minimo, tiempo_promedio_minutos)
                - por_maqueta (lista con estadísticas por maqueta)
                - progreso_temporal (dict con progreso por maqueta)
        """
        # Estadísticas básicas
        puntajes = [s.puntaje for s in sesiones]
        tiempos = [s.tiempo_segundos / 60 for s in sesiones]
        
        # Agrupar por maqueta
        por_maqueta = {}
        for sesion in sesiones:
            if sesion.maqueta not in por_maqueta:
                por_maqueta[sesion.maqueta] = []
            por_maqueta[sesion.maqueta].append(sesion)
        
        # Progreso temporal por maqueta (últimas 10 sesiones por maqueta)
        progreso_por_maqueta = {}
        for maqueta, sesiones_maqueta in por_maqueta.items():
            progreso_por_maqueta[maqueta] = []
            # Ordenar por fecha descendente y tomar últimas 10
            sesiones_ordenadas = sorted(sesiones_maqueta, key=lambda s: s.fecha, reverse=True)[:10]
            # Invertir para mostrar de más antigua a más reciente
            sesiones_ordenadas = sesiones_ordenadas[::-1]
            
            for sesion in sesiones_ordenadas:
                progreso_por_maqueta[maqueta].append({
                    'puntaje': sesion.puntaje,
                    'fecha': sesion.fecha.strftime('%d/%m'),
                    'fecha_completa': sesion.fecha.strftime('%Y-%m-%d')
                })
        
        return {
            'total_sesiones': len(sesiones),
            'estadisticas': {
                'puntaje_promedio': round(sum(puntajes) / len(puntajes), 2),
                'puntaje_maximo': max(puntajes),
                'puntaje_minimo': min(puntajes),
                'tiempo_promedio_minutos': round(sum(tiempos) / len(tiempos), 2)
            },
            'por_maqueta': self._agrupar_por_maqueta(por_maqueta),
            'progreso_temporal': progreso_por_maqueta
        }
    
    def _empty_analytics_response(self) -> Dict[str, Any]:
        """Respuesta vacía cuando no hay datos"""
        return {
            'success': False,
            'message': 'No hay datos disponibles para análisis',
            'estadisticas': {
                'general': {
                    'total_sesiones': 0,
                    'total_estudiantes': 0
                }
            },
            'ml_clasificacion': {'modelo_disponible': False},
            'ml_clustering': {'clusters': {}},
            'ml_correlaciones': {'disponible': False}
        }
    
    def _sesiones_to_dataframe_dict(self, sesiones: List) -> List[Dict[str, Any]]:
        """Convierte sesiones a formato dict para el analizador"""
        return [{
            'estudiante_id': s.estudiante_id,
            'estudiante_nombre': s.estudiante.nombre,
            'maqueta': s.maqueta,
            'puntaje': s.puntaje,
            'tiempo_segundos': s.tiempo_segundos,
            'interacciones_ia': s.interacciones_ia,
            'fecha': s.fecha
        } for s in sesiones]
    
    def _agrupar_por_maqueta(self, por_maqueta: Dict) -> List[Dict[str, Any]]:
        """Agrupa y calcula estadísticas por maqueta"""
        resultado = []
        
        for maqueta, sesiones in por_maqueta.items():
            puntajes = [s.puntaje for s in sesiones]
            resultado.append({
                'maqueta': maqueta,
                'sesiones': len(sesiones),
                'puntaje_promedio': round(sum(puntajes) / len(puntajes), 2),  # ✅ Cambiar 'promedio' → 'puntaje_promedio'
                'mejor': max(puntajes)
            })
        
        return resultado
    
    def _generar_insights_estudiante(self, sesiones: List) -> List[str]:
        """Genera insights personalizados para el estudiante"""
        insights = []
        
        puntajes = [s.puntaje for s in sesiones]
        promedio = sum(puntajes) / len(puntajes)
        
        if promedio >= 4:
            insights.append("¡Excelente desempeño! Mantén el buen trabajo.")
        elif promedio >= 3:
            insights.append("Buen rendimiento general. Sigue practicando.")
        else:
            insights.append("Hay margen de mejora. Considera repasar el contenido.")
        
        # Tendencia
        if len(sesiones) >= 3:
            ultimas_3 = puntajes[:3]
            promedio_reciente = sum(ultimas_3) / 3
            
            if promedio_reciente > promedio:
                insights.append("📈 Tendencia positiva: Estás mejorando.")
            elif promedio_reciente < promedio:
                insights.append("📉 Parece que has tenido dificultades recientes.")
        
        return insights
    
    def _serializar_sesiones(self, sesiones: List) -> List[Dict[str, Any]]:
        """Serializa sesiones para JSON"""
        return [{
            'id': s.id,
            'maqueta': s.maqueta,
            'puntaje': s.puntaje,
            'tiempo_segundos': s.tiempo_segundos,
            'interacciones_ia': s.interacciones_ia,
            'fecha': s.fecha.isoformat(),
            'profesor': {
                'id': s.profesor.id,
                'nombre': s.profesor.nombre
            } if s.profesor else None
        } for s in sesiones]
    
    def get_analytics_estudiante_por_profesor(self, estudiante_id: int, profesor_id: int) -> Dict[str, Any]:
        """
        Obtiene analytics de un estudiante filtrado por un profesor específico
        
        Args:
            estudiante_id: ID del estudiante
            profesor_id: ID del profesor
            
        Returns:
            Dict con analytics filtrados
        """
        from models import Sesion, Profesor
        
        # Verificar que el profesor existe
        profesor = Profesor.query.get(profesor_id)
        if not profesor:
            return {
                'success': False,
                'message': 'Profesor no encontrado'
            }
        
        # Obtener sesiones filtradas por profesor (objetos Sesion, no IDs)
        sesiones = Sesion.query.filter_by(
            estudiante_id=estudiante_id,
            profesor_id=profesor_id
        ).order_by(Sesion.fecha.desc()).all()
        
        if not sesiones:
            return {
                'success': True,
                'profesor': {
                    'id': profesor.id,
                    'nombre': profesor.nombre,
                    'institucion': profesor.institucion
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
                'insights': [f'No tienes sesiones registradas con {profesor.nombre} todavía'],
                'sesiones': []
            }
        
        # Calcular estadísticas base (lógica extraída - REFACTORIZADO)
        estadisticas_base = self._calcular_estadisticas_base(sesiones)
        
        # Insights personalizados con nombre del profesor
        insights = [f'📚 Sesiones con {profesor.nombre}']
        insights.extend(self._generar_insights_estudiante(sesiones))
        
        return {
            'success': True,
            'profesor': {
                'id': profesor.id,
                'nombre': profesor.nombre,
                'institucion': profesor.institucion
            },
            'total_sesiones': estadisticas_base['total_sesiones'],
            'estadisticas': estadisticas_base['estadisticas'],
            'por_maqueta': estadisticas_base['por_maqueta'],
            'progreso_temporal': estadisticas_base['progreso_temporal'],
            'insights': insights,
            'sesiones': self._serializar_sesiones(sesiones)
        }

