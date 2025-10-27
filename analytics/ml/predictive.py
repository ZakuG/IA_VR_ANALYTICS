"""
Módulo de Modelos Predictivos
Responsable de: predicción de rendimiento, clasificación binaria, regresión
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
from ..utils.converters import convert_to_native_types


class PredictiveModels:
    """Modelos predictivos de rendimiento estudiantil"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame con datos de sesiones
        """
        self.df = df
    
    def prediccion_rendimiento(self):
        """Modelo predictivo simple de rendimiento usando regresión lineal"""
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
            'formula': f"Puntaje = {round(model.intercept_, 2)} + "
                      f"({round(coef_tiempo, 4)}) * tiempo + "
                      f"({round(coef_ia, 4)}) * interacciones_ia"
        }
    
    @staticmethod
    def _interpretar_modelo(coef_tiempo, coef_ia, r2):
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
            'tiempo_segundos': float(rf_model.feature_importances_[0]),
            'interacciones_ia': float(rf_model.feature_importances_[1])
        }
        
        # Tasa de aprobación actual
        tasa_aprobacion = float((y == 1).sum() / len(y) * 100)
        
        # Interpretación
        interpretacion = self._generar_interpretacion_clasificacion(
            accuracy_lr, accuracy_rf, feature_importance
        )
        
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
    
    @staticmethod
    def _generar_interpretacion_clasificacion(accuracy_lr, accuracy_rf, feature_importance):
        """Genera interpretaciones de los modelos de clasificación"""
        interpretacion = []
        
        if accuracy_lr > 0.7 or accuracy_rf > 0.7:
            interpretacion.append(
                f"✅ Los modelos pueden predecir aprobación con "
                f"{max(accuracy_lr, accuracy_rf)*100:.1f}% de precisión"
            )
        else:
            interpretacion.append(
                f"⚠️ Precisión limitada ({max(accuracy_lr, accuracy_rf)*100:.1f}%). "
                "Se necesitan más datos"
            )
        
        if feature_importance['tiempo_segundos'] > feature_importance['interacciones_ia']:
            interpretacion.append("⏱️ El tiempo es el factor más importante para aprobar")
        else:
            interpretacion.append("🤖 El uso de IA es el factor más importante para aprobar")
        
        return interpretacion
