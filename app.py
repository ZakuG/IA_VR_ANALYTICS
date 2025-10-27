# app.py - Application Factory con Flask Blueprints
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar modelos y configuración de DB
from models import db, bcrypt, Profesor, Estudiante

# Importar registro de blueprints
from routes import register_blueprints

# Importar utilidades
from utils.logger import setup_logging

# ============================================
# CONFIGURACIÓN DE FLASK
# ============================================

app = Flask(__name__)

# Secret Key
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'tu_clave_secreta_aqui')

# Configuración de Base de Datos
database_url = os.getenv('DATABASE_URL', '').strip()

if database_url and database_url.startswith('postgresql'):
    # Usar PostgreSQL/Supabase
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'sslmode': 'require'
        }
    }
else:
    # Usar SQLite local por defecto
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "vr_analytics.db")}'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True
    }

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

# ============================================
# INICIALIZAR EXTENSIONES
# ============================================

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # ← Actualizado para usar blueprint

mail = Mail(app)

# Configurar logging
logger = setup_logging(app)

# ============================================
# FLASK-LOGIN USER LOADER
# ============================================

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario por su ID para Flask-Login"""
    if user_id.startswith('profesor_'):
        return Profesor.query.get(int(user_id.split('_')[1]))
    elif user_id.startswith('estudiante_'):
        return Estudiante.query.get(int(user_id.split('_')[1]))
    return None

# ============================================
# REGISTRAR BLUEPRINTS
# ============================================

register_blueprints(app)
logger.info("✅ Aplicación Flask inicializada con Blueprints")

# ============================================
# CREAR TABLAS (DESARROLLO)
# ============================================

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    with app.app_context():
        db.create_all()
        logger.info("✅ Tablas de base de datos creadas")

# ============================================
# EJECUTAR APLICACIÓN
# ============================================

if __name__ == '__main__':
    # Solo crear tablas en desarrollo local
    if os.getenv('FLASK_ENV') == 'development':
        init_db()
    
    # Obtener puerto de variable de entorno (para Render/Heroku)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)
