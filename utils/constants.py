"""
Constantes de la aplicación
Valores configurables y constantes del sistema
"""

# Validaciones
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 128
MIN_CODIGO_LENGTH = 3
MAX_CODIGO_LENGTH = 20

# Límites de sesión
MIN_PUNTAJE = 0.0
MAX_PUNTAJE = 7.0
PUNTAJE_APROBACION = 4.0  # Puntaje mínimo para aprobar
MAX_TIEMPO_SEGUNDOS = 7200  # 2 horas
MAX_INTERACCIONES_IA = 1000

# ML Constants
MIN_SESIONES_ML = 10
MIN_SESIONES_CLUSTERING = 5
MIN_SESIONES_CORRELACION = 3

# Mensajes
MSG_LOGIN_EXITOSO = "Inicio de sesión exitoso"
MSG_REGISTRO_EXITOSO = "Registro completado correctamente"
MSG_SESION_CREADA = "Sesión VR registrada correctamente"
MSG_ERROR_AUTENTICACION = "Credenciales incorrectas"
MSG_ERROR_PERMISOS = "No tienes permisos para acceder a este recurso"
MSG_CAMPOS_REQUERIDOS = "Todos los campos son requeridos"
MSG_PASSWORD_NO_COINCIDE = "Las contraseñas no coinciden"

# Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500

# Roles
ROLE_ESTUDIANTE = 'estudiante'
ROLE_PROFESOR = 'profesor'

# Configuración de Flask
SECRET_KEY_DEFAULT = 'dev-secret-key-change-in-production'
DATABASE_URI_DEFAULT = 'sqlite:///instance/vr_analytics.db'
