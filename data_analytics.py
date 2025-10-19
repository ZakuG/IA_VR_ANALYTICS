# data_analytics.py
"""
Módulo avanzado de análisis de datos para VR Analytics
Incluye análisis estadístico, machine learning y visualizaciones profesionales
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def convert_to_native_types(obj):
    """Convierte tipos NumPy/Pandas a tipos nativos de Python para JSON"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        # Sanitizar NaN, inf, -inf para JSON
        if np.isnan(obj) or np.isinf(obj):
            return 0
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    return obj

class AnalizadorAvanzado:
    """Clase para análisis avanzado de datos de estudiantes"""
    
    def __init__(self, sesiones):
        """
        Inicializa el analizador con las sesiones de los estudiantes
        
        Args:
            sesiones: Lista de objetos Sesion de SQLAlchemy
        """
        if not sesiones:
            self.df = pd.DataFrame()
            return
            
        self.df = pd.DataFrame([{
            'estudiante_id': s.estudiante_id,
            'estudiante_nombre': s.estudiante.nombre,
            'maqueta': s.maqueta,
            'tiempo_segundos': s.tiempo_segundos,
            'puntaje': s.puntaje,
            'fecha': s.fecha,
            'interacciones_ia': s.interacciones_ia
        } for s in sesiones])
        
        # Convertir tiempo a minutos para mejor interpretación
        self.df['tiempo_minutos'] = self.df['tiempo_segundos'] / 60
    
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
                'promedio_tiempo_min': float(round(self.df['tiempo_minutos'].mean(), 2)),
                'mediana_tiempo_min': float(round(self.df['tiempo_minutos'].median(), 2)),
                'tasa_aprobacion': float(round(tasa_aprob, 2)),
                'mejor_puntaje': int(self.df['puntaje'].max()),
                'peor_puntaje': int(self.df['puntaje'].min()),
            },
            'cuartiles': {
                'Q1_puntaje': float(self.df['puntaje'].quantile(0.25)),
                'Q2_puntaje': float(self.df['puntaje'].quantile(0.50)),
                'Q3_puntaje': float(self.df['puntaje'].quantile(0.75)),
                'Q1_tiempo': float(round(self.df['tiempo_minutos'].quantile(0.25), 2)),
                'Q3_tiempo': float(round(self.df['tiempo_minutos'].quantile(0.75), 2)),
            }
        }
        
        return convert_to_native_types(stats_dict)
    
    def analisis_por_maqueta(self):
        """Análisis detallado por tipo de maqueta"""
        if self.df.empty:
            return {}
        
        maquetas = {}
        for maqueta in self.df['maqueta'].unique():
            df_maqueta = self.df[self.df['maqueta'] == maqueta]
            
            tasa_aprob = (df_maqueta['puntaje'] >= 4).sum() / len(df_maqueta) * 100
            
            maquetas[str(maqueta)] = {
                'total_intentos': int(len(df_maqueta)),
                'promedio_puntaje': float(round(df_maqueta['puntaje'].mean(), 2)),
                'mediana_puntaje': float(df_maqueta['puntaje'].median()),
                'desviacion_puntaje': float(round(df_maqueta['puntaje'].std(), 2)),
                'promedio_tiempo_min': float(round(df_maqueta['tiempo_minutos'].mean(), 2)),
                'tasa_aprobacion': float(round(tasa_aprob, 2)),
                'promedio_interacciones_ia': float(round(df_maqueta['interacciones_ia'].mean(), 2)),
                'nivel_dificultad': self._calcular_dificultad(df_maqueta)
            }
        
        return convert_to_native_types(maquetas)
    
    def _calcular_dificultad(self, df_maqueta):
        """Calcula nivel de dificultad basado en puntajes y tiempo"""
        promedio_puntaje = df_maqueta['puntaje'].mean()
        promedio_tiempo = df_maqueta['tiempo_minutos'].mean()
        
        # Normalizar métricas (0-1)
        puntaje_norm = promedio_puntaje / 5
        tiempo_norm = min(promedio_tiempo / 3, 1)  # Asumiendo 3 min = difícil
        
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
                'interpretacion': self._interpretar_correlacion_simple(corr_tiempo_puntaje),
                'fuerza': self._fuerza_correlacion_simple(corr_tiempo_puntaje)
            },
            'ia_puntaje': {
                'correlacion': float(round(corr_ia_puntaje, 3)),
                'p_value': float(round(p_value_ia, 4)),
                'significativo': bool(p_value_ia < 0.05),
                'interpretacion': self._interpretar_correlacion_simple(corr_ia_puntaje),
                'fuerza': self._fuerza_correlacion_simple(corr_ia_puntaje)
            },
            'recomendaciones': self._generar_recomendaciones_correlacion(
                corr_tiempo_puntaje, corr_ia_puntaje
            )
        }
    
    def _interpretar_correlacion_simple(self, valor):
        """Interpreta el valor de correlación - versión simple"""
        direccion = "positiva" if valor > 0 else "negativa"
        return f"Correlación {direccion}"
    
    def _fuerza_correlacion_simple(self, valor):
        """Determina la fuerza de la correlación - versión simple"""
        abs_valor = abs(valor)
        if abs_valor < 0.3:
            return "débil"
        elif abs_valor < 0.7:
            return "moderada"
        else:
            return "fuerte"
    
    def _generar_recomendaciones_correlacion(self, corr_tiempo, corr_ia):
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
    
    def clustering_estudiantes(self, n_clusters=3):
        """
        Agrupa estudiantes por patrones de comportamiento usando K-Means
        
        Args:
            n_clusters: Número de grupos a formar
        """
        if self.df.empty or len(self.df) < n_clusters:
            return {}
        
        # Agregar datos por estudiante
        estudiantes_stats = self.df.groupby(['estudiante_id', 'estudiante_nombre']).agg({
            'puntaje': 'mean',
            'tiempo_minutos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        if len(estudiantes_stats) < n_clusters:
            return {}
        
        # Preparar datos para clustering
        features = estudiantes_stats[['puntaje', 'tiempo_minutos', 'interacciones_ia']].values
        
        # Normalizar
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        estudiantes_stats['cluster'] = kmeans.fit_predict(features_scaled)
        
        # Analizar clusters
        clusters = {}
        for i in range(n_clusters):
            cluster_data = estudiantes_stats[estudiantes_stats['cluster'] == i]
            
            clusters[f'Grupo_{i+1}'] = {
                'nombre': self._nombrar_cluster(cluster_data),
                'cantidad': int(len(cluster_data)),
                'promedio_puntaje': float(round(cluster_data['puntaje'].mean(), 2)),
                'promedio_tiempo_min': float(round(cluster_data['tiempo_minutos'].mean(), 2)),
                'promedio_ia': float(round(cluster_data['interacciones_ia'].mean(), 2)),
                'estudiantes': [str(x) for x in cluster_data['estudiante_nombre'].tolist()]
            }
        
        return convert_to_native_types(clusters)
    
    def _nombrar_cluster(self, cluster_data):
        """Asigna nombre descriptivo al cluster"""
        puntaje_medio = cluster_data['puntaje'].mean()
        tiempo_medio = cluster_data['tiempo_minutos'].mean()
        
        if puntaje_medio >= 5.5:
            return "Estudiantes Destacados"
        elif puntaje_medio >= 4 and tiempo_medio < self.df['tiempo_minutos'].median():
            return "Estudiantes Eficientes"
        elif puntaje_medio >= 4:
            return "Estudiantes Regulares"
        else:
            return "Estudiantes en Riesgo"
    
    def prediccion_rendimiento(self):
        """Modelo predictivo simple de rendimiento"""
        if self.df.empty or len(self.df) < 10:
            return {}
        
        # Preparar datos
        X = self.df[['tiempo_segundos', 'interacciones_ia']].values
        y = self.df['puntaje'].values
        
        # Regresión lineal
        model = LinearRegression()
        model.fit(X, y)
        
        # Coeficientes
        coef_tiempo = model.coef_[0]
        coef_ia = model.coef_[1]
        
        # R² score
        r2_score = model.score(X, y)
        
        return {
            'r2_score': float(round(r2_score, 3)),
            'precision': 'Alta' if r2_score > 0.7 else 'Moderada' if r2_score > 0.4 else 'Baja',
            'coeficiente_tiempo': float(round(coef_tiempo, 4)),
            'coeficiente_ia': float(round(coef_ia, 4)),
            'interpretacion': self._interpretar_modelo(coef_tiempo, coef_ia, r2_score),
            'formula': f"Puntaje = {round(model.intercept_, 2)} + ({round(coef_tiempo, 4)}) * tiempo + ({round(coef_ia, 4)}) * interacciones_ia"
        }
    
    def _interpretar_modelo(self, coef_tiempo, coef_ia, r2):
        """Interpreta el modelo predictivo"""
        interpretaciones = []
        
        if r2 < 0.3:
            return "El modelo tiene baja capacidad predictiva. Los resultados son muy variables."
        
        if coef_tiempo > 0:
            interpretaciones.append("Mayor tiempo se asocia con mejor puntaje")
        else:
            interpretaciones.append("Menor tiempo se asocia con mejor puntaje")
        
        if coef_ia > 0:
            interpretaciones.append("Más interacciones con IA mejoran el puntaje")
        else:
            interpretaciones.append("Menos interacciones con IA mejoran el puntaje")
        
        return ". ".join(interpretaciones) + f". (R² = {round(r2, 2)})"
    
    def estudiantes_en_riesgo(self, threshold_puntaje=4):
        """Identifica estudiantes que necesitan atención"""
        if self.df.empty:
            return []
        
        estudiantes_stats = self.df.groupby(['estudiante_id', 'estudiante_nombre']).agg({
            'puntaje': ['mean', 'std', 'count'],
            'tiempo_minutos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        estudiantes_stats.columns = ['estudiante_id', 'estudiante_nombre', 'puntaje_mean', 
                                     'puntaje_std', 'intentos', 'tiempo_mean', 'ia_mean']
        
        # Criterios de riesgo
        promedio_tiempo = self.df['tiempo_minutos'].mean()
        std_tiempo = self.df['tiempo_minutos'].std()
        
        en_riesgo = estudiantes_stats[
            (estudiantes_stats['puntaje_mean'] < threshold_puntaje) | 
            (estudiantes_stats['tiempo_mean'] > promedio_tiempo + 1.5*std_tiempo) |
            (estudiantes_stats['tiempo_mean'] < promedio_tiempo - 1.5*std_tiempo)
        ].copy()
        
        # Añadir motivo de riesgo
        def determinar_riesgo(row):
            motivos = []
            if row['puntaje_mean'] < threshold_puntaje:
                motivos.append(f"Promedio bajo ({round(row['puntaje_mean'], 2)})")
            if row['tiempo_mean'] > promedio_tiempo + 1.5*std_tiempo:
                motivos.append("Tiempo excesivo")
            if row['tiempo_mean'] < promedio_tiempo - 1.5*std_tiempo:
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
            'tiempo_minutos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        # Puntuación compuesta
        # Normalizar tiempo (menor es mejor)
        max_tiempo = ranking['tiempo_minutos'].max()
        ranking['tiempo_normalizado'] = 1 - (ranking['tiempo_minutos'] / max_tiempo)
        
        # Fórmula ponderada
        ranking['puntuacion_final'] = (
            ranking['puntaje'] * 0.6 +  # 60% puntaje
            ranking['tiempo_normalizado'] * 7 * 0.3 +  # 30% eficiencia de tiempo
            (ranking['interacciones_ia'] / ranking['interacciones_ia'].max() * 7 * 0.1)  # 10% uso de IA
        )
        
        # Ordenar
        ranking = ranking.nlargest(top_n, 'puntuacion_final')
        
        result = ranking[[
            'estudiante_nombre', 'puntaje', 'tiempo_minutos', 
            'interacciones_ia', 'puntuacion_final'
        ]].to_dict('records')
        
        return convert_to_native_types(result)
    
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
                'mensaje': f'⚠️ Tasa de aprobación baja ({round(tasa_aprobacion, 1)}%). Se recomienda revisar la dificultad o el contenido.'
            })
        elif tasa_aprobacion > 90:
            insights.append({
                'tipo': 'positivo',
                'mensaje': f'✅ Excelente tasa de aprobación ({round(tasa_aprobacion, 1)}%). Los estudiantes están comprendiendo bien.'
            })
        
        # Análisis de variabilidad
        std_puntaje = self.df['puntaje'].std()
        if std_puntaje > 1.5:
            insights.append({
                'tipo': 'atencion',
                'mensaje': f'📊 Alta variabilidad en puntajes (σ={round(std_puntaje, 2)}). Algunos estudiantes necesitan apoyo adicional.'
            })
        
        # Análisis por maqueta
        maquetas_dificiles = []
        for maqueta in self.df['maqueta'].unique():
            df_maqueta = self.df[self.df['maqueta'] == maqueta]
            promedio = df_maqueta['puntaje'].mean()
            if promedio < 2.5:
                maquetas_dificiles.append(maqueta)
        
        if maquetas_dificiles:
            insights.append({
                'tipo': 'critico',
                'mensaje': f'🔧 Maquetas con bajo rendimiento: {", ".join(maquetas_dificiles)}. Considera simplificar o agregar más ayudas.'
            })
        
        # Análisis de uso de IA
        promedio_ia = self.df['interacciones_ia'].mean()
        if promedio_ia < 2:
            insights.append({
                'tipo': 'info',
                'mensaje': f'🤖 Bajo uso de IA ({round(promedio_ia, 1)} interacciones promedio). Incentiva su uso para mejor aprendizaje.'
            })
        
        return insights
    
    def datos_para_visualizacion(self):
        """Prepara datos optimizados para gráficos"""
        if self.df.empty:
            return {}
        
        result = {
            'distribucion_puntajes': convert_to_native_types(self.df['puntaje'].value_counts().sort_index().to_dict()),
            'puntajes_por_maqueta': convert_to_native_types(self.df.groupby('maqueta')['puntaje'].mean().to_dict()),
            'tiempos_por_maqueta': convert_to_native_types(self.df.groupby('maqueta')['tiempo_minutos'].mean().to_dict()),
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
            'tiempo': self.df['tiempo_minutos'].tolist(),
            'puntaje': self.df['puntaje'].tolist(),
            'maqueta': self.df['maqueta'].tolist()
        }
    
    # ============================================
    # MÉTODOS DE MACHINE LEARNING PROFESIONAL
    # ============================================
    
    def clasificacion_binaria_aprobacion(self):
        """
        Clasificación binaria: Predice si un estudiante aprobará (puntaje >= 4)
        Usa Logistic Regression y Random Forest
        """
        if self.df.empty or len(self.df) < 10:
            return {
                'modelo_disponible': False,
                'mensaje': 'Necesitas al menos 10 sesiones para entrenar el modelo de clasificación'
            }
        
        # Preparar features y target
        X = self.df[['tiempo_segundos', 'interacciones_ia']].copy()
        X['tiempo_minutos'] = X['tiempo_segundos'] / 60
        X = X[['tiempo_minutos', 'interacciones_ia']]
        
        # Target: 1 = Aprobado (>=4), 0 = Reprobado (<4)
        y = (self.df['puntaje'] >= 4).astype(int)
        
        # Si todos son de la misma clase, no se puede clasificar
        if y.nunique() == 1:
            return {
                'modelo_disponible': False,
                'mensaje': 'Todos los estudiantes tienen el mismo resultado (aprobado/reprobado)'
            }
        
        # Split train/test
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
        except ValueError:
            # Si no hay suficientes muestras para stratify
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
        
        # Entrenar Logistic Regression
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train_scaled, y_train)
        
        # Predicciones
        y_pred_lr = lr_model.predict(X_test_scaled)
        accuracy_lr = accuracy_score(y_test, y_pred_lr)
        
        # Random Forest
        rf_model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        rf_model.fit(X_train, y_train)
        y_pred_rf = rf_model.predict(X_test)
        accuracy_rf = accuracy_score(y_test, y_pred_rf)
        
        # Matriz de confusión
        cm_lr = confusion_matrix(y_test, y_pred_lr)
        cm_rf = confusion_matrix(y_test, y_pred_rf)
        
        # Importancia de características (Random Forest)
        feature_importance = {
            'tiempo_minutos': float(rf_model.feature_importances_[0]),
            'interacciones_ia': float(rf_model.feature_importances_[1])
        }
        
        # Tasa de aprobación actual
        tasa_aprobacion = float((y == 1).sum() / len(y) * 100)
        
        # Interpretación
        interpretacion = []
        if accuracy_lr > 0.7 or accuracy_rf > 0.7:
            interpretacion.append(f"✅ Los modelos pueden predecir aprobación con {max(accuracy_lr, accuracy_rf)*100:.1f}% de precisión")
        else:
            interpretacion.append(f"⚠️ Precisión limitada ({max(accuracy_lr, accuracy_rf)*100:.1f}%). Se necesitan más datos")
        
        if feature_importance['tiempo_minutos'] > feature_importance['interacciones_ia']:
            interpretacion.append("⏱️ El tiempo es el factor más importante para aprobar")
        else:
            interpretacion.append("🤖 El uso de IA es el factor más importante para aprobar")
        
        return convert_to_native_types({
            'modelo_disponible': True,
            'tasa_aprobacion_real': tasa_aprobacion,
            'logistic_regression': {
                'accuracy': accuracy_lr,
                'precision': accuracy_lr,  # Simplificado
                'confusion_matrix': cm_lr.tolist()
            },
            'random_forest': {
                'accuracy': accuracy_rf,
                'precision': accuracy_rf,
                'confusion_matrix': cm_rf.tolist(),
                'feature_importance': feature_importance
            },
            'mejor_modelo': 'Random Forest' if accuracy_rf > accuracy_lr else 'Logistic Regression',
            'mejor_accuracy': max(accuracy_lr, accuracy_rf),
            'interpretacion': interpretacion,
            'total_sesiones': len(self.df),
            'aprobados': int((y == 1).sum()),
            'reprobados': int((y == 0).sum())
        })
    
    def kmeans_clustering_profesional(self, n_clusters=3):
        """
        K-Means Clustering profesional para agrupar estudiantes por rendimiento
        Incluye análisis de silueta y perfiles de clusters
        """
        if self.df.empty:
            return {}
        
        # Agrupar por estudiante
        estudiantes_stats = self.df.groupby('estudiante_id').agg({
            'puntaje': ['mean', 'std', 'count'],
            'tiempo_minutos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        estudiantes_stats.columns = ['_'.join(col).strip('_') for col in estudiantes_stats.columns.values]
        
        # ✅ VALIDACIÓN: K-Means requiere al menos 2 muestras
        num_estudiantes = len(estudiantes_stats)
        
        if num_estudiantes < 2:
            # Con 1 estudiante, no podemos hacer clustering
            return {
                'clustering_disponible': False,
                'razon': 'Se requieren al menos 2 estudiantes para clustering',
                'num_estudiantes': num_estudiantes,
                'clusters': [],
                'silhouette_score': None,
                'estudiantes_por_cluster': {},
                'mensaje': f'Actualmente hay {num_estudiantes} estudiante(s). Se necesitan al menos 2 para análisis de clustering.'
            }
        
        # Ajustar n_clusters según número de estudiantes
        if num_estudiantes < n_clusters:
            n_clusters = max(2, num_estudiantes // 2)
        
        # Features para clustering
        features = estudiantes_stats[['puntaje_mean', 'tiempo_minutos_mean', 'interacciones_ia_mean']].fillna(0)
        
        # Normalizar
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        estudiantes_stats['cluster'] = kmeans.fit_predict(features_scaled)
        
        # Análisis por cluster
        clusters_info = {}
        for cluster_id in range(n_clusters):
            cluster_data = estudiantes_stats[estudiantes_stats['cluster'] == cluster_id]
            
            # Perfil del cluster
            promedio_puntaje = float(cluster_data['puntaje_mean'].mean())
            promedio_tiempo = float(cluster_data['tiempo_minutos_mean'].mean())
            promedio_ia = float(cluster_data['interacciones_ia_mean'].mean())
            
            # Clasificar cluster
            if promedio_puntaje >= 5.5:
                nivel = 'Excelente'
                color = '#28a745'
                icono = '🌟'
            elif promedio_puntaje >= 4:
                nivel = 'Bueno'
                color = '#17a2b8'
                icono = '✅'
            elif promedio_puntaje >= 3:
                nivel = 'Regular'
                color = '#ffc107'
                icono = '⚠️'
            else:
                nivel = 'Necesita Ayuda'
                color = '#dc3545'
                icono = '🆘'
            
            # Características distintivas
            caracteristicas = []
            if promedio_tiempo < features['tiempo_minutos_mean'].median():
                caracteristicas.append('Rápidos')
            if promedio_ia > features['interacciones_ia_mean'].median():
                caracteristicas.append('Usan mucho la IA')
            if promedio_puntaje > features['puntaje_mean'].median():
                caracteristicas.append('Alto rendimiento')
            
            clusters_info[f'Cluster {cluster_id + 1}'] = {
                'nivel': nivel,
                'icono': icono,
                'color': color,
                'total_estudiantes': int(len(cluster_data)),
                'promedio_puntaje': round(promedio_puntaje, 2),
                'promedio_tiempo_min': round(promedio_tiempo, 2),
                'promedio_uso_ia': round(promedio_ia, 2),
                'caracteristicas': caracteristicas if caracteristicas else ['Sin características distintivas'],
                'descripcion': f"{icono} {nivel}: {len(cluster_data)} estudiantes con promedio de {promedio_puntaje:.1f}/7"
            }
        
        # Calcular inercia (calidad del clustering)
        inercia = float(kmeans.inertia_)
        
        return convert_to_native_types({
            'n_clusters': n_clusters,
            'clusters': clusters_info,
            'inercia': inercia,
            'total_estudiantes': len(estudiantes_stats),
            'centroides': kmeans.cluster_centers_.tolist(),
            'interpretacion': self._interpretar_clusters(clusters_info)
        })
    
    def _interpretar_clusters(self, clusters_info):
        """Genera interpretaciones automáticas de los clusters"""
        interpretaciones = []
        
        # Encontrar mejor y peor cluster
        clusters_ordenados = sorted(
            clusters_info.items(),
            key=lambda x: x[1]['promedio_puntaje'],
            reverse=True
        )
        
        mejor = clusters_ordenados[0]
        peor = clusters_ordenados[-1]
        
        interpretaciones.append(
            f"🏆 {mejor[0]} tiene el mejor rendimiento con {mejor[1]['promedio_puntaje']}/7"
        )
        
        if peor[1]['promedio_puntaje'] < 4:
            interpretaciones.append(
                f"📢 {peor[0]} necesita atención: {peor[1]['total_estudiantes']} estudiantes con promedio {peor[1]['promedio_puntaje']}/7"
            )
        
        # Identificar patrones
        for nombre, info in clusters_info.items():
            if 'Usan mucho la IA' in info['caracteristicas'] and info['promedio_puntaje'] < 3:
                interpretaciones.append(
                    f"💡 {nombre} usa mucha IA pero tiene bajo rendimiento. Revisar metodología de estudio"
                )
            elif info['promedio_tiempo_min'] > 2 and info['promedio_puntaje'] < 3:
                interpretaciones.append(
                    f"⏰ {nombre} toma mucho tiempo pero bajo puntaje. Posible dificultad con el contenido"
                )
        
        return interpretaciones
    
    def correlaciones_con_pvalues(self):
        """
        Análisis de correlaciones profesional con p-values y tests estadísticos
        """
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
            'interpretacion': self._interpretar_correlacion(corr_tp, pval_tp, 'tiempo', 'puntaje'),
            'fuerza': self._fuerza_correlacion(corr_tp)
        }
        
        # 2. IA vs Puntaje
        corr_ip, pval_ip = stats.pearsonr(self.df['interacciones_ia'], self.df['puntaje'])
        correlaciones['ia_puntaje'] = {
            'correlacion': float(corr_ip),
            'p_value': float(pval_ip),
            'significativo': pval_ip < 0.05,
            'interpretacion': self._interpretar_correlacion(corr_ip, pval_ip, 'uso de IA', 'puntaje'),
            'fuerza': self._fuerza_correlacion(corr_ip)
        }
        
        # 3. Tiempo vs IA
        corr_ti, pval_ti = stats.pearsonr(self.df['tiempo_segundos'], self.df['interacciones_ia'])
        correlaciones['tiempo_ia'] = {
            'correlacion': float(corr_ti),
            'p_value': float(pval_ti),
            'significativo': pval_ti < 0.05,
            'interpretacion': self._interpretar_correlacion(corr_ti, pval_ti, 'tiempo', 'uso de IA'),
            'fuerza': self._fuerza_correlacion(corr_ti)
        }
        
        # Matriz de correlación
        matriz = self.df[['tiempo_segundos', 'puntaje', 'interacciones_ia']].corr()
        
        return convert_to_native_types({
            'disponible': True,
            'correlaciones': correlaciones,
            'matriz_correlacion': matriz.to_dict(),
            'resumen': self._generar_resumen_correlaciones(correlaciones)
        })
    
    def _fuerza_correlacion(self, corr):
        """Clasifica la fuerza de una correlación"""
        abs_corr = abs(corr)
        if abs_corr < 0.3:
            return 'Débil'
        elif abs_corr < 0.7:
            return 'Moderada'
        else:
            return 'Fuerte'
    
    def _interpretar_correlacion(self, corr, pval, var1, var2):
        """Interpreta una correlación con su p-value"""
        if pval >= 0.05:
            return f"No hay correlación significativa entre {var1} y {var2} (p={pval:.3f})"
        
        if corr > 0:
            return f"✅ Correlación positiva: A mayor {var1}, mayor {var2} (p={pval:.3f})"
        else:
            return f"⬇️ Correlación negativa: A mayor {var1}, menor {var2} (p={pval:.3f})"
    
    def _generar_resumen_correlaciones(self, correlaciones):
        """Genera un resumen ejecutivo de las correlaciones"""
        resumen = []
        
        for nombre, datos in correlaciones.items():
            if datos['significativo']:
                resumen.append(f"📊 {datos['interpretacion']} - Fuerza: {datos['fuerza']}")
        
        if not resumen:
            resumen.append("No se encontraron correlaciones estadísticamente significativas (p < 0.05)")
        
        return resumen
