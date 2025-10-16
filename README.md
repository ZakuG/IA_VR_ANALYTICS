# VR Analytics - Sistema de Análisis de Datos para Simuladores VR Educativos

Sistema web desarrollado en Flask para que profesores puedan registrarse y analizar el rendimiento de sus estudiantes en simuladores de realidad virtual educativos.

## 🎯 Características

- **Registro y autenticación de profesores**
- **Dashboard interactivo** con visualizaciones avanzadas
- **Análisis estadístico completo** (correlaciones, tendencias, predicciones)
- **Machine Learning**:
  - Clustering de estudiantes (K-Means)
  - Modelo predictivo de rendimiento (Regresión Lineal)
- **Identificación automática** de estudiantes en riesgo
- **Análisis por maqueta** (Aire acondicionado, Motor, etc.)
- **Insights automáticos** basados en los datos
- **API REST** para integración con Unity/Meta Quest

## 📊 Análisis de Data Science Incluidos

1. **Estadísticas Descriptivas**: Media, mediana, desviación estándar, cuartiles
2. **Análisis de Correlaciones**: Pearson con tests de significancia
3. **Clustering**: Agrupación de estudiantes por patrones de comportamiento
4. **Regresión Lineal**: Predicción de puntajes basada en tiempo e interacciones IA
5. **Detección de Outliers**: Identificación de estudiantes atípicos
6. **Tendencias Temporales**: Evolución del rendimiento en el tiempo

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o ubicarse en el directorio del proyecto**

2. **Instalar dependencias**:
```powershell
pip install -r requirements.txt
```

3. **Generar datos de prueba** (opcional, para demostración):
```powershell
python generate_test_data.py
```

4. **Ejecutar la aplicación**:
```powershell
python app.py
```

5. **Abrir el navegador** en: http://localhost:5000

## 👤 Credenciales de Prueba

Si ejecutaste `generate_test_data.py`:
- **Email**: profesor@test.com
- **Password**: 123456

## 📁 Estructura del Proyecto

```
Sonet_Version/
├── app.py                  # Aplicación Flask principal
├── data_analytics.py       # Módulo de análisis avanzado
├── generate_test_data.py   # Script para generar datos de prueba
├── requirements.txt        # Dependencias del proyecto
├── instance/
│   └── vr_analytics.db    # Base de datos SQLite (se crea automáticamente)
└── templates/
    ├── index.html         # Página de inicio
    ├── login.html         # Página de login
    ├── register.html      # Página de registro
    └── dashboard.html     # Dashboard principal con análisis
```

## 🔌 API para Unity

### Endpoint para registrar sesiones desde Unity

**POST** `/api/unity/session`

```json
{
  "codigo_estudiante": "EST001",
  "maqueta": "Aire acondicionado",
  "tiempo_segundos": 85,
  "puntaje": 4,
  "interacciones_ia": 3,
  "respuestas": [
    {"pregunta": 1, "respuesta": "A", "correcta": true},
    {"pregunta": 2, "respuesta": "B", "correcta": true}
  ]
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "session_id": 123
}
```

### Ejemplo de código C# para Unity

```csharp
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

[System.Serializable]
public class SessionData
{
    public string codigo_estudiante;
    public string maqueta;
    public int tiempo_segundos;
    public int puntaje;
    public int interacciones_ia;
}

public class VRAnalyticsIntegration : MonoBehaviour
{
    private string apiUrl = "http://localhost:5000/api/unity/session";

    public IEnumerator EnviarResultados(string codigoEstudiante, string maqueta, 
                                       int tiempoSegundos, int puntaje, int interaccionesIA)
    {
        SessionData data = new SessionData
        {
            codigo_estudiante = codigoEstudiante,
            maqueta = maqueta,
            tiempo_segundos = tiempoSegundos,
            puntaje = puntaje,
            interacciones_ia = interaccionesIA
        };

        string jsonData = JsonUtility.ToJson(data);
        
        UnityWebRequest request = new UnityWebRequest(apiUrl, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Resultados enviados correctamente");
        }
        else
        {
            Debug.LogError("Error: " + request.error);
        }
    }
}
```

## 📊 Análisis Disponibles en el Dashboard

### 1. Estadísticas Generales
- Total de sesiones
- Promedio de puntaje
- Tasa de aprobación
- Tiempo promedio
- Desviación estándar

### 2. Análisis de Correlaciones
- Tiempo vs Puntaje (con test de significancia)
- Interacciones IA vs Puntaje
- Recomendaciones automáticas

### 3. Clustering de Estudiantes
Agrupa automáticamente a los estudiantes en:
- **Estudiantes Destacados**: Alto rendimiento
- **Estudiantes Eficientes**: Buen rendimiento en poco tiempo
- **Estudiantes Regulares**: Rendimiento promedio
- **Estudiantes en Riesgo**: Requieren atención

### 4. Modelo Predictivo
- Ecuación de predicción de puntaje
- Coeficientes de impacto
- Precisión del modelo (R²)

### 5. Visualizaciones
- Distribución de puntajes (gráfico de barras)
- Rendimiento por maqueta (gráfico radar)
- Relación tiempo vs puntaje (scatter plot)
- Tendencia temporal (gráfico de líneas)

### 6. Insights Automáticos
El sistema genera automáticamente recomendaciones como:
- Identificación de maquetas difíciles
- Detección de bajo uso de IA
- Alertas de baja tasa de aprobación
- Sugerencias de mejora

## 🔒 Seguridad

- Contraseñas encriptadas con bcrypt
- Sesiones seguras con Flask-Login
- Autenticación requerida para acceso a datos
- Validación de datos en backend

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Bcrypt
- **Data Science**: Pandas, NumPy, SciPy, Scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Visualización**: Chart.js
- **Base de Datos**: SQLite

## 📈 Mejoras Futuras Sugeridas

1. **Exportación de reportes** en PDF/Excel
2. **Comparación entre grupos** de estudiantes
3. **Notificaciones por email** para estudiantes en riesgo
4. **Análisis de sentimiento** de interacciones con IA
5. **Dashboard en tiempo real** con WebSockets
6. **Más algoritmos de ML** (Random Forest, SVM, etc.)
7. **Análisis de secuencias** de aprendizaje

## 👥 Gestión de Estudiantes

Los profesores pueden:
- Registrar nuevos estudiantes
- Ver historial completo de cada estudiante
- Identificar estudiantes que necesitan atención
- Ver rankings de rendimiento

## 📝 Notas para tu Profesora

Este sistema implementa múltiples técnicas de **Data Science**:

1. **Análisis Exploratorio de Datos (EDA)**: Estadísticas descriptivas completas
2. **Inferencia Estadística**: Tests de correlación de Pearson con p-values
3. **Machine Learning Supervisado**: Regresión lineal para predicción
4. **Machine Learning No Supervisado**: K-Means clustering
5. **Visualización de Datos**: Múltiples tipos de gráficos interactivos
6. **Feature Engineering**: Normalización y transformación de datos
7. **Interpretación de Resultados**: Insights automáticos y recomendaciones

Los datos se correlacionan de manera realista:
- Estudiantes más rápidos tienden a tener mejores puntajes (si conocen el tema)
- Más interacciones con IA pueden indicar dificultad o interés
- El tiempo excesivo puede indicar confusión o dedicación

## 🆘 Soporte

Para problemas o preguntas sobre el sistema, revisa los logs en la consola o abre un issue.

## 📄 Licencia

Este proyecto es para fines educativos.
