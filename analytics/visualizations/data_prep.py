"""
Módulo de Preparación de Datos para Visualizaciones
Responsable de: formatear datos para gráficos, tendencias temporales, scatter plots
"""

import pandas as pd
from ..utils.converters import convert_to_native_types


class VisualizationDataPrep:
    """Preparación de datos para gráficos y visualizaciones"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame con datos de sesiones
        """
        self.df = df
    
    def datos_para_visualizacion(self):
        """Prepara datos optimizados para gráficos"""
        if self.df.empty:
            return {}
        
        result = {
            'distribucion_puntajes': convert_to_native_types(
                self.df['puntaje'].value_counts().sort_index().to_dict()
            ),
            'puntajes_por_maqueta': convert_to_native_types(
                self.df.groupby('maqueta')['puntaje'].mean().to_dict()
            ),
            'tiempos_por_maqueta': convert_to_native_types(
                self.df.groupby('maqueta')['tiempo_segundos'].mean().to_dict()
            ),
            'tendencia_temporal': self._preparar_tendencia_temporal(),
            'scatter_tiempo_puntaje': self._preparar_scatter()
        }
        return convert_to_native_types(result)
    
    def _preparar_tendencia_temporal(self):
        """Prepara datos de tendencia temporal"""
        self.df['fecha'] = pd.to_datetime(self.df['fecha'])
        tendencia = self.df.set_index('fecha').resample('D')['puntaje'].mean()
        
        return {
            'fechas': [str(d.date()) for d in tendencia.index],
            'puntajes': [float(p) if not pd.isna(p) else 0 for p in tendencia.values]
        }
    
    def _preparar_scatter(self):
        """Prepara datos para scatter plot"""
        return {
            'tiempo': self.df['tiempo_segundos'].tolist(),
            'puntaje': self.df['puntaje'].tolist(),
            'maqueta': self.df['maqueta'].tolist(),
            'estudiante': self.df['estudiante_nombre'].tolist()
        }
