"""
Módulo de Clustering y Segmentación
Responsable de: K-Means clustering, silhouette score, segmentación de estudiantes
"""

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from ..utils.converters import convert_to_native_types


class ClusteringAnalyzer:
    """Análisis de clustering para segmentación de estudiantes"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame con datos de sesiones
        """
        self.df = df
    
    def clustering_estudiantes(self, n_clusters=3):
        """
        Agrupa estudiantes por patrones de comportamiento usando K-Means (OPTIMIZADO)
        
        Args:
            n_clusters: Número de grupos a formar
        """
        if self.df.empty or len(self.df) < n_clusters:
            return {}
        
        # Agregar datos por estudiante (una sola operación)
        estudiantes_stats = self.df.groupby(['estudiante_id', 'estudiante_nombre']).agg({
            'puntaje': 'mean',
            'tiempo_segundos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        num_estudiantes = len(estudiantes_stats)
        
        if num_estudiantes < 2:
            return {
                'clustering_disponible': False,
                'razon': 'Se requieren al menos 2 estudiantes para clustering',
                'num_estudiantes': num_estudiantes
            }
        
        # Ajustar n_clusters al número de estudiantes disponibles
        n_clusters = min(n_clusters, max(2, num_estudiantes // 2))
        
        # Preparar datos para clustering
        features = estudiantes_stats[['puntaje', 'tiempo_segundos', 'interacciones_ia']].values
        
        # Normalizar
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_scaled)
        
        # OPTIMIZACIÓN: Calcular silhouette score (métrica de calidad)
        silhouette_avg = silhouette_score(features_scaled, labels) if num_estudiantes > n_clusters else 0
        
        # Analizar clusters
        clusters = {}
        for i in range(n_clusters):
            mask = labels == i
            cluster_data = estudiantes_stats[mask]
            
            clusters[f'Grupo_{i+1}'] = {
                'nombre': self._nombrar_cluster(cluster_data),
                'cantidad': int(len(cluster_data)),
                'promedio_puntaje': float(round(cluster_data['puntaje'].mean(), 2)),
                'promedio_tiempo_segundos': float(round(cluster_data['tiempo_segundos'].mean(), 2)),
                'promedio_ia': float(round(cluster_data['interacciones_ia'].mean(), 2)),
                'estudiantes': [str(x) for x in cluster_data['estudiante_nombre'].tolist()]
            }
        
        # OPTIMIZACIÓN: Retornar métricas adicionales
        return convert_to_native_types({
            'clustering_disponible': True,
            'n_clusters': n_clusters,
            'clusters': clusters,
            'silhouette_score': round(silhouette_avg, 3),
            'calidad': 'Excelente' if silhouette_avg > 0.7 else 'Buena' if silhouette_avg > 0.5 else 'Moderada',
            'total_estudiantes': num_estudiantes
        })
    
    def _nombrar_cluster(self, cluster_data):
        """Asigna nombre descriptivo al cluster"""
        puntaje_medio = cluster_data['puntaje'].mean()
        tiempo_medio = cluster_data['tiempo_segundos'].mean()
        
        if puntaje_medio >= 6:
            return "Estudiantes Destacados"
        elif puntaje_medio >= 5 and tiempo_medio < self.df['tiempo_segundos'].median():
            return "Estudiantes Eficientes"
        elif puntaje_medio >= 4:
            return "Estudiantes Regulares"
        else:
            return "Estudiantes en Riesgo"
    
    def kmeans_clustering_profesional(self, n_clusters=3):
        """
        K-Means Clustering profesional para agrupar estudiantes por rendimiento
        Incluye análisis de silueta y perfiles de clusters
        """
        if self.df.empty:
            return {}
        
        # Agrupar por estudiante
        estudiantes_stats = self.df.groupby(['estudiante_id', 'estudiante_nombre']).agg({
            'puntaje': ['mean', 'std', 'count'],
            'tiempo_segundos': 'mean',
            'interacciones_ia': 'mean'
        }).reset_index()
        
        # Renombrar columnas para facilitar acceso
        estudiantes_stats.columns = ['estudiante_id', 'estudiante_nombre', 'puntaje_mean', 
                                     'puntaje_std', 'puntaje_count', 'tiempo_segundos_mean', 
                                     'interacciones_ia_mean']
        
        # VALIDACIÓN: K-Means requiere al menos 2 muestras
        num_estudiantes = len(estudiantes_stats)
        
        if num_estudiantes < 2:
            return {
                'clustering_disponible': False,
                'razon': 'Se requieren al menos 2 estudiantes para clustering',
                'num_estudiantes': num_estudiantes,
                'clusters': [],
                'silhouette_score': None,
                'estudiantes_por_cluster': {},
                'mensaje': f'Actualmente hay {num_estudiantes} estudiante(s). '
                          'Se necesitan al menos 2 para análisis de clustering.'
            }
        
        # Ajustar n_clusters según número de estudiantes
        if num_estudiantes < n_clusters:
            n_clusters = max(2, num_estudiantes // 2)
        
        # Features para clustering
        features = estudiantes_stats[['puntaje_mean', 'tiempo_segundos_mean', 'interacciones_ia_mean']].fillna(0)
        
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
            promedio_tiempo = float(cluster_data['tiempo_segundos_mean'].mean())
            promedio_ia = float(cluster_data['interacciones_ia_mean'].mean())
            
            # Clasificar cluster
            nivel, color, icono = self._clasificar_cluster(promedio_puntaje)
            
            # Características distintivas
            caracteristicas = self._identificar_caracteristicas(
                promedio_tiempo, promedio_ia, features
            )
            
            # ✅ NUEVO: Agregar lista de estudiantes
            estudiantes_del_cluster = cluster_data['estudiante_nombre'].tolist()
            
            clusters_info[f'Cluster {cluster_id + 1}'] = {
                'nivel': nivel,
                'icono': icono,
                'color': color,
                'total_estudiantes': int(len(cluster_data)),
                'promedio_puntaje': round(promedio_puntaje, 2),
                'promedio_tiempo_segundos': round(promedio_tiempo, 2),
                'promedio_uso_ia': round(promedio_ia, 2),
                'caracteristicas': caracteristicas if caracteristicas else ['Sin características distintivas'],
                'descripcion': f"{icono} {nivel}: {len(cluster_data)} estudiantes con promedio de {promedio_puntaje:.1f}/7",
                'estudiantes': [str(e) for e in estudiantes_del_cluster]  # ✅ Lista de nombres
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
    
    @staticmethod
    def _clasificar_cluster(promedio_puntaje):
        """Clasifica el nivel del cluster según promedio de puntaje"""
        if promedio_puntaje >= 6:
            return 'Excelente', '#28a745', '🌟'
        elif promedio_puntaje >= 5:
            return 'Bueno', '#17a2b8', '✅'
        elif promedio_puntaje >= 4:
            return 'Regular', '#ffc107', '⚠️'
        else:
            return 'Necesita Ayuda', '#dc3545', '🆘'
    
    @staticmethod
    def _identificar_caracteristicas(promedio_tiempo, promedio_ia, features):
        """Identifica características distintivas del cluster"""
        caracteristicas = []
        
        if promedio_tiempo < features['tiempo_segundos_mean'].median():
            caracteristicas.append('Rápidos')
        if promedio_ia > features['interacciones_ia_mean'].median():
            caracteristicas.append('Usan mucho la IA')
        
        return caracteristicas
    
    @staticmethod
    def _interpretar_clusters(clusters_info):
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
            f"🏆 {mejor[0]} tiene el mejor rendimiento con {mejor[1]['promedio_puntaje']}/7.0"
        )
        
        if peor[1]['promedio_puntaje'] < 4:
            interpretaciones.append(
                f"📢 {peor[0]} necesita atención: "
                f"{peor[1]['total_estudiantes']} estudiantes con promedio {peor[1]['promedio_puntaje']}/7.0"
            )
        
        # Identificar patrones
        for nombre, info in clusters_info.items():
            if 'Usan mucho la IA' in info['caracteristicas'] and info['promedio_puntaje'] < 4:
                interpretaciones.append(
                    f"💡 {nombre} usa mucha IA pero tiene bajo rendimiento. Revisar metodología de estudio"
                )
            elif info['promedio_tiempo_segundos'] > 120 and info['promedio_puntaje'] < 4:
                interpretaciones.append(
                    f"⏰ {nombre} toma mucho tiempo pero bajo puntaje. Posible dificultad con el contenido"
                )
        
        return interpretaciones
