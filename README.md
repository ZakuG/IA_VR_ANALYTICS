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
- **API REST**

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

2. **Crear y activar entorno virtual** (recomendado):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. **Instalar dependencias**:
```powershell
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
   - Copia `.env.example` a `.env`
   - Configura las variables necesarias

5. **Inicializar base de datos** (si es necesario):
```powershell
python scripts/migrate_db.py
```

6. **Generar datos de prueba** (opcional, para demostración):
```powershell
python scripts/generate_test_data.py
```

7. **Ejecutar la aplicación**:
```powershell
python app.py
```

8. **Abrir el navegador** en: http://localhost:5000

## 👤 Credenciales de Prueba

Si ejecutaste `generate_test_data.py`:
- **Email**: profesor@test.com
- **Password**: 123456

## 📁 Estructura del Proyecto

```
Sonet_Version/
├── app.py                      # Aplicación Flask principal
├── requirements.txt            # Dependencias del proyecto
├── pyproject.toml             # Configuración del proyecto
│
├── models/                    # Modelos de datos (SQLAlchemy)
│   ├── usuario.py
│   ├── profesor.py
│   ├── estudiante.py
│   └── sesion.py
│
├── routes/                    # Rutas de la aplicación
│   ├── auth_routes.py        # Autenticación
│   ├── profesor_routes.py    # Endpoints de profesor
│   ├── estudiante_routes.py  # Endpoints de estudiante
│   └── api_routes.py         # API REST
│
├── services/                  # Lógica de negocio
│   ├── auth_service.py
│   ├── analytics_service.py
│   └── ml_service.py
│
├── repositories/              # Acceso a datos
│   ├── profesor_repository.py
│   ├── estudiante_repository.py
│   └── sesion_repository.py
│
├── static/                    # Archivos estáticos
│   ├── css/                  # Estilos
│   ├── js/                   # JavaScript
│   └── images/               # Imágenes
│
├── templates/                 # Plantillas HTML
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── dashboard_estudiante.html
│
├── scripts/                   # Scripts de utilidad
│   ├── README.md
│   ├── generate_test_data.py
│   ├── migrate_db.py
│   ├── test_db_connection.py
│   └── verificar_profesores.py
│
├── docs/                      # Documentación
│   ├── ARQUITECTURA_SOFTWARE.md
│   ├── ARQUITECTURA_AUTH.md
│   ├── DIAGRAMAS_VISUALES.md
│   └── PRESENTACION_EJECUTIVA.md
│
├── tests/                     # Pruebas unitarias
├── logs/                      # Logs de la aplicación
├── instance/                  # Base de datos
│   └── vr_analytics.db
│
└── utils/                     # Utilidades generales
```

## 🔌 API

### Endpoint para registrar sesiones

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

## 👥 Gestión de Estudiantes

Los profesores pueden:
- Registrar nuevos estudiantes
- Ver historial completo de cada estudiante
- Identificar estudiantes que necesitan atención
- Ver rankings de rendimiento

## 🆘 Soporte

Para problemas o preguntas sobre el sistema, revisa los logs en la consola o abre un issue.

## 📄 Licencia

Este proyecto es para fines educativos.
