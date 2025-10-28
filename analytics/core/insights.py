"""
Módulo de Insights y Análisis de Estudiantes
Responsable de: insights automáticos, estudiantes en riesgo, rankings
"""

import pandas as pd
from ..utils.converters import convert_to_native_types


class InsightsGenerator:
    """Generador de insights y análisis de rendimiento estudiantil"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame con datos de sesiones
        """
        self.df = df
    
    def generar_insights(self):
        """Genera insights automáticos basados en los datos"""
        if self.df.empty:
            return []
        
        insights = []
        
        # Análisis de tasa de aprobación
        tasa_aprobacion = (self.df['puntaje'] >= 4).sum() / len(self.df) * 100
        if tasa_aprobacion < 50:
            insights.append({
                'tipo': 'critico',
                'mensaje': f'⚠️ Tasa de aprobación baja ({round(tasa_aprobacion, 1)}%). '
                          'Se recomienda revisar la dificultad o el contenido.'
            })
        elif tasa_aprobacion > 90:
            insights.append({
                'tipo': 'positivo',
                'mensaje': f'✅ Excelente tasa de aprobación ({round(tasa_aprobacion, 1)}%). '
                          'Los estudiantes están comprendiendo bien.'
            })
        
        # Análisis de variabilidad
        std_puntaje = self.df['puntaje'].std()
        # Manejar NaN cuando solo hay 1 sesión
        if pd.notna(std_puntaje) and std_puntaje > 1.5:
            insights.append({
                'tipo': 'atencion',
                'mensaje': f'📊 Alta variabilidad en puntajes (σ={round(std_puntaje, 2)}). '
                          'Algunos estudiantes necesitan apoyo adicional.'
            })
        
        # Análisis por maqueta
        maquetas_dificiles = []
        for maqueta in self.df['maqueta'].unique():
            df_maqueta = self.df[self.df['maqueta'] == maqueta]
            promedio = df_maqueta['puntaje'].mean()
            if promedio < 4:
                maquetas_dificiles.append(maqueta)
        
        if maquetas_dificiles:
            insights.append({
                'tipo': 'critico',
                'mensaje': f'🔧 Maquetas con bajo rendimiento: {", ".join(maquetas_dificiles)}. '
                          'Considera simplificar o agregar más ayudas.'
            })
        
        # Análisis de uso de IA
        promedio_ia = self.df['interacciones_ia'].mean()
        if promedio_ia < 2:
            insights.append({
                'tipo': 'info',
                'mensaje': f'🤖 Bajo uso de IA ({round(promedio_ia, 1)} interacciones promedio). '
                          'Incentiva su uso para mejor aprendizaje.'
            })
        
        return insights
    
    def estudiantes_en_riesgo(self, threshold_puntaje=4):
        """Identifica estudiantes que necesitan atención"""
        if self.df.empty:
            return []
        
        estudiantes_stats = self.df.groupby(['estudiante_id', 'estudiante_nombre']).agg({
            'puntaje': ['mean', 'std', 'count'],
            'tiempo_segundos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        estudiantes_stats.columns = [
            'estudiante_id', 'estudiante_nombre', 'puntaje_mean', 
            'puntaje_std', 'intentos', 'tiempo_mean', 'ia_mean'
        ]
        
        # Criterios de riesgo
        promedio_tiempo = self.df['tiempo_segundos'].mean()
        std_tiempo = self.df['tiempo_segundos'].std()
        
        en_riesgo = estudiantes_stats[
            (estudiantes_stats['puntaje_mean'] < threshold_puntaje) | 
            (estudiantes_stats['tiempo_mean'] > promedio_tiempo + 1.5 * std_tiempo) |
            (estudiantes_stats['tiempo_mean'] < promedio_tiempo - 1.5 * std_tiempo)
        ].copy()
        
        # Añadir motivo de riesgo
        def determinar_riesgo(row):
            motivos = []
            if row['puntaje_mean'] < threshold_puntaje:
                motivos.append(f"Promedio bajo ({round(row['puntaje_mean'], 2)})")
            if row['tiempo_mean'] > promedio_tiempo + 1.5 * std_tiempo:
                motivos.append("Tiempo excesivo")
            if row['tiempo_mean'] < promedio_tiempo - 1.5 * std_tiempo:
                motivos.append("Tiempo muy bajo (posible apuro)")
            return ", ".join(motivos)
        
        if not en_riesgo.empty:
            en_riesgo['motivo_riesgo'] = en_riesgo.apply(determinar_riesgo, axis=1)
        
        return convert_to_native_types(en_riesgo.to_dict('records'))
    
    def ranking_estudiantes(self, top_n=10):
        """Ranking de estudiantes por rendimiento global"""
        if self.df.empty:
            return []
        
        ranking = self.df.groupby(['estudiante_id', 'estudiante_nombre']).agg({
            'puntaje': 'mean',
            'tiempo_segundos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        # Puntuación compuesta
        # Normalizar tiempo (menor es mejor)
        max_tiempo = ranking['tiempo_segundos'].max()
        ranking['tiempo_normalizado'] = 1 - (ranking['tiempo_segundos'] / max_tiempo)
        
        # Fórmula ponderada
        ranking['puntuacion_final'] = (
            ranking['puntaje'] * 0.6 +  # 60% puntaje
            ranking['tiempo_normalizado'] * 7 * 0.3 +  # 30% eficiencia de tiempo
            (ranking['interacciones_ia'] / ranking['interacciones_ia'].max() * 7 * 0.1)  # 10% uso de IA
        )
        
        # Ordenar
        ranking = ranking.nlargest(top_n, 'puntuacion_final')
        
        result = ranking[[
            'estudiante_nombre', 'puntaje', 'tiempo_segundos', 
            'interacciones_ia', 'puntuacion_final'
        ]].to_dict('records')
        
        return convert_to_native_types(result)
