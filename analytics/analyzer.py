"""
Analizador Avanzado - Facade Pattern
Orquesta todos los módulos de análisis de forma cohesiva
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from .core.statistics import EstadisticasAnalyzer
from .core.insights import InsightsGenerator
from .ml.clustering import ClusteringAnalyzer
from .ml.predictive import PredictiveModels
from .visualizations.data_prep import VisualizationDataPrep


class AnalizadorAvanzado:
    """
    Clase principal para análisis avanzado de datos de estudiantes
    
    Arquitectura Modular:
    - EstadisticasAnalyzer: Estadísticas descriptivas y correlaciones
    - InsightsGenerator: Insights automáticos y rankings
    - ClusteringAnalyzer: K-Means clustering y segmentación
    - PredictiveModels: Modelos predictivos y clasificación
    - VisualizationDataPrep: Preparación de datos para gráficos
    """
    
    def __init__(self, sesiones):
        """
        Inicializa el analizador con las sesiones de los estudiantes
        
        Args:
            sesiones: Lista de objetos Sesion de SQLAlchemy
        """
        if not sesiones:
            self.df = pd.DataFrame()
        else:
            self.df = pd.DataFrame([{
                'estudiante_id': s.estudiante_id,
                'estudiante_nombre': s.estudiante.nombre,
                'maqueta': s.maqueta,
                'tiempo_segundos': s.tiempo_segundos,
                'puntaje': s.puntaje,
                'fecha': s.fecha,
                'interacciones_ia': s.interacciones_ia
            } for s in sesiones])
        
        # Inicializar módulos especializados
        self._estadisticas = EstadisticasAnalyzer(self.df)
        self._insights = InsightsGenerator(self.df)
        self._clustering = ClusteringAnalyzer(self.df)
        self._predictive = PredictiveModels(self.df)
        self._visualization = VisualizationDataPrep(self.df)
    
    # ============================================
    # MÉTODOS DE ESTADÍSTICAS DESCRIPTIVAS
    # ============================================
    
    def estadisticas_descriptivas(self):
        """Estadísticas descriptivas completas"""
        return self._estadisticas.estadisticas_descriptivas()
    
    def analisis_por_maqueta(self):
        """Análisis detallado por tipo de maqueta"""
        return self._estadisticas.analisis_por_maqueta()
    
    def correlaciones_avanzadas(self):
        """Análisis de correlaciones con interpretaciones"""
        return self._estadisticas.correlaciones_avanzadas()
    
    def correlaciones_con_pvalues(self):
        """Análisis de correlaciones profesional con p-values"""
        return self._estadisticas.correlaciones_con_pvalues()
    
    # ============================================
    # MÉTODOS DE INSIGHTS Y RANKINGS
    # ============================================
    
    def generar_insights(self):
        """Genera insights automáticos basados en los datos"""
        return self._insights.generar_insights()
    
    def estudiantes_en_riesgo(self, threshold_puntaje=4):
        """Identifica estudiantes que necesitan atención"""
        return self._insights.estudiantes_en_riesgo(threshold_puntaje)
    
    def ranking_estudiantes(self, top_n=10):
        """Ranking de estudiantes por rendimiento global"""
        return self._insights.ranking_estudiantes(top_n)
    
    # ============================================
    # MÉTODOS DE MACHINE LEARNING - CLUSTERING
    # ============================================
    
    def clustering_estudiantes(self, n_clusters=3):
        """Agrupa estudiantes por patrones de comportamiento usando K-Means"""
        return self._clustering.clustering_estudiantes(n_clusters)
    
    def kmeans_clustering_profesional(self, n_clusters=3):
        """K-Means Clustering profesional con análisis de silueta"""
        return self._clustering.kmeans_clustering_profesional(n_clusters)
    
    # ============================================
    # MÉTODOS DE MACHINE LEARNING - PREDICTIVO
    # ============================================
    
    def prediccion_rendimiento(self):
        """Modelo predictivo simple de rendimiento"""
        return self._predictive.prediccion_rendimiento()
    
    def clasificacion_binaria_aprobacion(self):
        """Clasificación binaria: Predice si un estudiante aprobará"""
        return self._predictive.clasificacion_binaria_aprobacion()
    
    # ============================================
    # MÉTODOS DE VISUALIZACIÓN
    # ============================================
    
    def datos_para_visualizacion(self):
        """Prepara datos optimizados para gráficos"""
        return self._visualization.datos_para_visualizacion()
    
    # ============================================
    # PROPIEDADES
    # ============================================
    
    @property
    def tiene_datos(self):
        """Verifica si hay datos disponibles"""
        return not self.df.empty
    
    @property
    def total_sesiones(self):
        """Retorna el número total de sesiones"""
        return len(self.df)
    
    @property
    def total_estudiantes(self):
        """Retorna el número total de estudiantes únicos"""
        return self.df['estudiante_id'].nunique() if not self.df.empty else 0
