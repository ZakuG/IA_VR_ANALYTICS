"""
Módulo de Estadísticas y Análisis Descriptivo
Responsable de: estadísticas descriptivas, análisis por maqueta, correlaciones
"""

import pandas as pd
from scipy import stats
from ..utils.converters import convert_to_native_types


class EstadisticasAnalyzer:
    """Análisis estadístico descriptivo y correlaciones"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame con datos de sesiones
        """
        self.df = df
    
    def estadisticas_descriptivas(self):
        """Estadísticas descriptivas completas"""
        if self.df.empty:
            return {}
        
        tasa_aprob = (self.df['puntaje'] >= 4).sum() / len(self.df) * 100
        
        stats_dict = {
            'general': {
                'total_sesiones': int(len(self.df)),
                'total_estudiantes': int(self.df['estudiante_id'].nunique()),
                'promedio_puntaje': float(round(self.df['puntaje'].mean(), 2)),
                'mediana_puntaje': float(self.df['puntaje'].median()),
                'desviacion_puntaje': float(round(self.df['puntaje'].std(), 2)),
                'varianza_puntaje': float(round(self.df['puntaje'].var(), 2)),
                'promedio_tiempo_segundos': float(round(self.df['tiempo_segundos'].mean(), 2)),
                'mediana_tiempo_segundos': float(round(self.df['tiempo_segundos'].median(), 2)),
                'tasa_aprobacion': float(round(tasa_aprob, 2)),
                'mejor_puntaje': int(self.df['puntaje'].max()),
                'peor_puntaje': int(self.df['puntaje'].min()),
            },
            'cuartiles': {
                'Q1_puntaje': float(self.df['puntaje'].quantile(0.25)),
                'Q2_puntaje': float(self.df['puntaje'].quantile(0.50)),
                'Q3_puntaje': float(self.df['puntaje'].quantile(0.75)),
                'Q1_tiempo': float(round(self.df['tiempo_segundos'].quantile(0.25), 2)),
                'Q3_tiempo': float(round(self.df['tiempo_segundos'].quantile(0.75), 2)),
            }
        }
        
        return convert_to_native_types(stats_dict)
    
    def analisis_por_maqueta(self):
        """Análisis detallado por tipo de maqueta (OPTIMIZADO con groupby múltiple)"""
        if self.df.empty:
            return {}
        
        # OPTIMIZACIÓN: Una sola operación groupby para TODAS las métricas
        agg_dict = {
            'puntaje': ['count', 'mean', 'median', 'std'],
            'tiempo_segundos': 'mean',
            'interacciones_ia': 'mean'
        }
        
        grouped = self.df.groupby('maqueta').agg(agg_dict)
        
        maquetas = {}
        for maqueta in grouped.index:
            row = grouped.loc[maqueta]
            
            total = int(row[('puntaje', 'count')])
            promedio = float(row[('puntaje', 'mean')])
            
            # Calcular tasa de aprobación para esta maqueta
            mask = self.df['maqueta'] == maqueta
            tasa_aprobacion = (self.df.loc[mask, 'puntaje'] >= 4).sum() / total * 100
            
            maquetas[str(maqueta)] = {
                'total_intentos': total,
                'promedio_puntaje': round(promedio, 2),
                'mediana_puntaje': float(row[('puntaje', 'median')]),
                'desviacion_puntaje': round(float(row[('puntaje', 'std')]), 2),
                'promedio_tiempo_segundos': round(float(row[('tiempo_segundos', 'mean')]), 2),
                'tasa_aprobacion': round(tasa_aprobacion, 2),
                'promedio_interacciones_ia': round(float(row[('interacciones_ia', 'mean')]), 2),
                'nivel_dificultad': self._calcular_dificultad(promedio, float(row[('tiempo_segundos', 'mean')]))
            }
        
        return convert_to_native_types(maquetas)
    
    @staticmethod
    def _calcular_dificultad(promedio_puntaje: float, promedio_tiempo: float) -> str:
        """Calcula nivel de dificultad basado en puntajes y tiempo"""
        # Normalizar métricas (0-1)
        puntaje_norm = promedio_puntaje / 7
        tiempo_norm = min(promedio_tiempo / 240, 1)  # 240 segundos (4 min) = difícil
        
        # Dificultad inversa al puntaje, directa al tiempo
        dificultad = ((1 - puntaje_norm) + tiempo_norm) / 2
        
        if dificultad < 0.3:
            return 'Fácil'
        elif dificultad < 0.6:
            return 'Moderada'
        else:
            return 'Difícil'
    
    def correlaciones_avanzadas(self):
        """Análisis de correlaciones con interpretaciones"""
        if self.df.empty or len(self.df) < 3:
            return {}
        
        # Correlaciones de Pearson
        corr_tiempo_puntaje = self.df['tiempo_segundos'].corr(self.df['puntaje'])
        corr_ia_puntaje = self.df['interacciones_ia'].corr(self.df['puntaje'])
        
        # Test de significancia
        _, p_value_tiempo = stats.pearsonr(self.df['tiempo_segundos'], self.df['puntaje'])
        _, p_value_ia = stats.pearsonr(self.df['interacciones_ia'], self.df['puntaje'])
        
        return {
            'tiempo_puntaje': {
                'correlacion': float(round(corr_tiempo_puntaje, 3)),
                'p_value': float(round(p_value_tiempo, 4)),
                'significativo': bool(p_value_tiempo < 0.05),
                'interpretacion': self._interpretar_correlacion(corr_tiempo_puntaje),
                'fuerza': self._fuerza_correlacion(corr_tiempo_puntaje)
            },
            'ia_puntaje': {
                'correlacion': float(round(corr_ia_puntaje, 3)),
                'p_value': float(round(p_value_ia, 4)),
                'significativo': bool(p_value_ia < 0.05),
                'interpretacion': self._interpretar_correlacion(corr_ia_puntaje),
                'fuerza': self._fuerza_correlacion(corr_ia_puntaje)
            },
            'recomendaciones': self._generar_recomendaciones(corr_tiempo_puntaje, corr_ia_puntaje)
        }
    
    @staticmethod
    def _interpretar_correlacion(valor: float) -> str:
        """Interpreta el valor de correlación"""
        direccion = "positiva" if valor > 0 else "negativa"
        return f"Correlación {direccion}"
    
    @staticmethod
    def _fuerza_correlacion(valor: float) -> str:
        """Determina la fuerza de la correlación"""
        abs_valor = abs(valor)
        if abs_valor < 0.3:
            return "débil"
        elif abs_valor < 0.7:
            return "moderada"
        else:
            return "fuerte"
    
    @staticmethod
    def _generar_recomendaciones(corr_tiempo: float, corr_ia: float) -> list:
        """Genera recomendaciones basadas en correlaciones"""
        recomendaciones = []
        
        if corr_tiempo < -0.3:
            recomendaciones.append(
                "Los estudiantes más rápidos tienden a obtener mejores puntajes. "
                "Considera optimizar el contenido para reducir tiempos innecesarios."
            )
        elif corr_tiempo > 0.3:
            recomendaciones.append(
                "Más tiempo dedicado se asocia con mejores resultados. "
                "Los estudiantes podrían beneficiarse de más tiempo para explorar."
            )
        
        if corr_ia > 0.3:
            recomendaciones.append(
                "Las interacciones con la IA mejoran el rendimiento. "
                "Incentiva a los estudiantes a usar más esta herramienta."
            )
        elif corr_ia < -0.3:
            recomendaciones.append(
                "Muchas interacciones con IA se asocian con puntajes más bajos. "
                "Podría indicar confusión - revisa la claridad del contenido."
            )
        
        if not recomendaciones:
            recomendaciones.append("No se encontraron correlaciones fuertes. Los resultados son variados.")
        
        return recomendaciones
    
    def correlaciones_con_pvalues(self):
        """Análisis de correlaciones profesional con p-values y tests estadísticos"""
        if self.df.empty or len(self.df) < 3:
            return {
                'disponible': False,
                'mensaje': 'Se necesitan al menos 3 sesiones para calcular correlaciones'
            }
        
        correlaciones = {}
        
        # 1. Tiempo vs Puntaje
        corr_tp, pval_tp = stats.pearsonr(self.df['tiempo_segundos'], self.df['puntaje'])
        correlaciones['tiempo_puntaje'] = {
            'correlacion': float(corr_tp),
            'p_value': float(pval_tp),
            'significativo': pval_tp < 0.05,
            'interpretacion': self._interpretar_correlacion_detallada(corr_tp, pval_tp, 'tiempo', 'puntaje'),
            'fuerza': self._fuerza_correlacion(corr_tp)
        }
        
        # 2. IA vs Puntaje
        corr_ip, pval_ip = stats.pearsonr(self.df['interacciones_ia'], self.df['puntaje'])
        correlaciones['ia_puntaje'] = {
            'correlacion': float(corr_ip),
            'p_value': float(pval_ip),
            'significativo': pval_ip < 0.05,
            'interpretacion': self._interpretar_correlacion_detallada(corr_ip, pval_ip, 'uso de IA', 'puntaje'),
            'fuerza': self._fuerza_correlacion(corr_ip)
        }
        
        # 3. Tiempo vs IA
        corr_ti, pval_ti = stats.pearsonr(self.df['tiempo_segundos'], self.df['interacciones_ia'])
        correlaciones['tiempo_ia'] = {
            'correlacion': float(corr_ti),
            'p_value': float(pval_ti),
            'significativo': pval_ti < 0.05,
            'interpretacion': self._interpretar_correlacion_detallada(corr_ti, pval_ti, 'tiempo', 'uso de IA'),
            'fuerza': self._fuerza_correlacion(corr_ti)
        }
        
        # Matriz de correlación
        matriz = self.df[['tiempo_segundos', 'puntaje', 'interacciones_ia']].corr()
        
        return convert_to_native_types({
            'disponible': True,
            'correlaciones': correlaciones,
            'matriz_correlacion': matriz.to_dict(),
            'resumen': correlaciones
        })
    
    @staticmethod
    def _interpretar_correlacion_detallada(corr: float, pval: float, var1: str, var2: str) -> str:
        """Interpreta una correlación con detalle"""
        if pval >= 0.05:
            return f"No hay correlación significativa entre {var1} y {var2}"
        
        if corr > 0:
            return f"✅ Correlación positiva: A mayor {var1}, mayor {var2}"
        else:
            return f"⬇️ Correlación negativa: A mayor {var1}, menor {var2}"
