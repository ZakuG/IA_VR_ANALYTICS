# VR Analytics Platform - Arquitectura POO

## 📁 Estructura del Proyecto

```
Sonet_Version/
├── app.py                      # Punto de entrada principal
├── data_analytics.py           # Motor de análisis y ML
├── models.py                   # Modelos SQLAlchemy
│
├── repositories/               # 🗄️ Capa de Acceso a Datos
│   ├── __init__.py
│   ├── session_repository.py  # CRUD de sesiones
│   ├── estudiante_repository.py # CRUD de estudiantes
│   └── profesor_repository.py # CRUD de profesores
│
├── services/                   # 🧠 Capa de Lógica de Negocio
│   ├── __init__.py
│   ├── analytics_service.py   # Servicio de análisis
│   ├── session_service.py     # Servicio de sesiones
│   └── auth_service.py        # Servicio de autenticación
│
├── utils/                      # 🛠️ Utilidades
│   ├── __init__.py
│   ├── constants.py           # Constantes del sistema
│   ├── validators.py          # Validadores de datos
│   └── decorators.py          # Decoradores de rutas
│
├── templates/                  # 🎨 Vistas HTML
│   ├── dashboard.html
│   └── dashboard_estudiante.html
│
└── instance/                   # 💾 Base de datos
    └── vr_analytics.db
```

## 🏗️ Arquitectura en Capas

### **Capa 1: Modelos (ORM)**
- **Ubicación**: `models.py`
- **Responsabilidad**: Representación de entidades de BD
- **Tecnología**: SQLAlchemy ORM
- **Clases**:
  - `Estudiante`
  - `Profesor`
  - `Sesion`

### **Capa 2: Repositorios (Data Access)**
- **Ubicación**: `repositories/`
- **Responsabilidad**: Abstracción de acceso a datos
- **Patrón**: Repository Pattern
- **Características**:
  - Métodos CRUD tipados
  - Validación de datos
  - Queries complejas encapsuladas
  - Sin lógica de negocio

**Ejemplo de uso**:
```python
from repositories import SessionRepository

# Crear sesión
sesion = SessionRepository.create(
    estudiante_id=1,
    maqueta="Maqueta A",
    puntaje=4.5,
    tiempo_segundos=180,
    interacciones_ia=5
)

# Obtener sesiones
sesiones = SessionRepository.get_by_profesor(profesor_id=1)
```

### **Capa 3: Servicios (Business Logic)**
- **Ubicación**: `services/`
- **Responsabilidad**: Lógica de negocio compleja
- **Patrón**: Service Layer Pattern
- **Características**:
  - Orquestación de múltiples repositorios
  - Validaciones de negocio
  - Transformación de datos
  - Manejo de errores

**Ejemplo de uso**:
```python
from services import AnalyticsService

analytics_service = AnalyticsService()

# Obtener análisis completo
analytics = analytics_service.get_analytics_profesor(profesor_id=1)

# Incluye: estadísticas, ML, visualizaciones, recomendaciones
```

### **Capa 4: Controladores (Routes)**
- **Ubicación**: `app.py`
- **Responsabilidad**: Manejo de HTTP requests/responses
- **Características**:
  - Decoradores de autenticación
  - Validación de JSON
  - Serialización de respuestas
  - Manejo de errores HTTP

**Ejemplo**:
```python
@app.route('/api/analytics')
@login_required_profesor
def get_analytics():
    analytics_service = AnalyticsService()
    data = analytics_service.get_analytics_profesor(
        current_user.id
    )
    return jsonify(data)
```

## 🎯 Principios SOLID Aplicados

### **Single Responsibility Principle (SRP)**
✅ Cada clase tiene **una única responsabilidad**:
- `SessionRepository` → Solo acceso a datos de sesiones
- `AnalyticsService` → Solo lógica de análisis
- `AuthService` → Solo autenticación

### **Open/Closed Principle (OCP)**
✅ Abierto a extensión, cerrado a modificación:
- Nuevos repositorios sin modificar existentes
- Nuevos servicios sin cambiar routes

### **Liskov Substitution Principle (LSP)**
✅ Interfaces consistentes:
- Todos los repositorios siguen mismo patrón
- Métodos `get_by_id()`, `create()`, `delete()`

### **Interface Segregation Principle (ISP)**
✅ Interfaces específicas:
- Servicios especializados (`AnalyticsService`, `AuthService`)
- No clases monolíticas

### **Dependency Inversion Principle (DIP)**
✅ Dependencias de abstracciones:
- Services dependen de Repositories (interfaces)
- Routes dependen de Services

## 📦 Componentes Principales

### **1. SessionRepository**
```python
# CRUD completo de sesiones
create(estudiante_id, maqueta, puntaje, ...)
get_by_id(sesion_id)
get_by_estudiante(estudiante_id)
get_by_profesor(profesor_id)
get_by_maqueta(maqueta, profesor_id=None)
get_estadisticas_profesor(profesor_id)
delete(sesion_id)
```

### **2. AnalyticsService**
```python
# Análisis completo
get_analytics_profesor(profesor_id)
  ├── Estadísticas generales
  ├── Visualizaciones (Chart.js)
  ├── Clustering K-means
  ├── Clasificación binaria
  ├── Correlaciones con p-values
  └── Recomendaciones personalizadas

get_analytics_estudiante(estudiante_id)
  ├── Progreso temporal
  ├── Insights personalizados
  └── Análisis por maqueta
```

### **3. AuthService**
```python
# Autenticación y autorización
login_estudiante(codigo, password)
login_profesor(email, password)
register_estudiante(...)
register_profesor(...)
inscribir_estudiante_profesor(...)
```

## 🔧 Utilidades

### **Validadores** (`utils/validators.py`)
```python
validate_email(email) → (bool, mensaje)
validate_codigo(codigo) → (bool, mensaje)
validate_password(password) → (bool, mensaje)
validate_puntaje(puntaje) → (bool, mensaje)
validate_tiempo(tiempo_segundos) → (bool, mensaje)
```

### **Decoradores** (`utils/decorators.py`)
```python
@login_required_profesor       # Solo profesores
@login_required_estudiante     # Solo estudiantes
@login_required                # Cualquier usuario
@validate_json(['campo1'])     # Valida JSON request
```

### **Constantes** (`utils/constants.py`)
```python
# Validaciones
MIN_PASSWORD_LENGTH = 4
MAX_PUNTAJE = 5.0

# Mensajes
MSG_LOGIN_EXITOSO = "Inicio de sesión exitoso"

# HTTP Status
HTTP_OK = 200
HTTP_UNAUTHORIZED = 401
```

## 🚀 Ventajas de esta Arquitectura

### **Mantenibilidad**
✅ Código organizado en capas lógicas
✅ Fácil localizar y modificar funcionalidad
✅ Cambios aislados (sin efectos secundarios)

### **Testabilidad**
✅ Cada capa testeable independientemente
✅ Mocks fáciles de crear
✅ Test unitarios y de integración claros

### **Escalabilidad**
✅ Agregar nuevas features sin tocar código existente
✅ Fácil migrar a microservicios
✅ Múltiples bases de datos posibles

### **Reutilización**
✅ Servicios reutilizables en diferentes contextos
✅ Repositorios compartidos
✅ Validadores centralizados

### **Legibilidad**
✅ Código auto-documentado
✅ Nombres descriptivos
✅ Responsabilidades claras

## 📖 Ejemplos de Uso

### **Crear una sesión (Completo)**
```python
# 1. Validar datos
validation = validate_puntaje(4.5)
if not validation[0]:
    return {"error": validation[1]}

# 2. Usar servicio
session_service = SessionService()
result = session_service.create_session(
    estudiante_codigo="EST001",
    maqueta="Maqueta VR A",
    puntaje=4.5,
    tiempo_segundos=180,
    interacciones_ia=5,
    profesor_email="prof@example.com"
)

# 3. Responder
if result['success']:
    return jsonify(result), 201
else:
    return jsonify(result), 400
```

### **Obtener analytics (Clean)**
```python
@app.route('/api/analytics')
@login_required_profesor
def get_analytics():
    service = AnalyticsService()
    data = service.get_analytics_profesor(session['user_id'])
    return jsonify(data)
```

## 🔄 Flujo de una Request

```
1. Request HTTP
   ↓
2. Route (@app.route)
   ↓
3. Decorador de autenticación
   ↓
4. Validación de datos
   ↓
5. Servicio (lógica de negocio)
   ↓
6. Repository (acceso a datos)
   ↓
7. Database (SQLAlchemy ORM)
   ↓
8. Response JSON
```

## 🎓 Mejores Prácticas Implementadas

1. ✅ **Type Hints** - Todos los métodos tipados
2. ✅ **Docstrings** - Documentación en cada función
3. ✅ **Error Handling** - Try/except con mensajes claros
4. ✅ **Validation** - Validación en capas múltiples
5. ✅ **DRY** - No repetir código
6. ✅ **KISS** - Mantenerlo simple
7. ✅ **YAGNI** - Solo lo necesario

## 🔮 Próximos Pasos

- [ ] Blueprints para organizar routes
- [ ] Tests unitarios con pytest
- [ ] Logging profesional
- [ ] API REST con OpenAPI/Swagger
- [ ] Cache con Redis
- [ ] Paginación de resultados
- [ ] Rate limiting
- [ ] Websockets para tiempo real

---

**Desarrollado con principios de Clean Code y POO** 🚀
