"""
Configuración de fixtures para pytest
"""
import sys
import os
import pytest
import tempfile

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app
from models import db


@pytest.fixture
def app():
    """Crea una aplicación Flask de prueba con BD en memoria"""
    # Crear BD temporal
    db_fd, db_path = tempfile.mkstemp()
    
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Crear tablas
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()
    
    # Limpiar
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Cliente de prueba para hacer requests"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner para comandos de Flask"""
    return app.test_cli_runner()
