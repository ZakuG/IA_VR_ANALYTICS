"""
Tests configuration and fixtures
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app, db
from models import Profesor, Estudiante, Sesion


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Configure test database
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def profesor_test(app):
    """Create a test profesor."""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    
    profesor = Profesor(
        nombre='Profesor Test',
        email='test@profesor.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        institucion='USS'
    )
    db.session.add(profesor)
    db.session.commit()
    return profesor


@pytest.fixture
def estudiante_test(app):
    """Create a test estudiante."""
    from flask_bcrypt import Bcrypt
    bcrypt = Bcrypt()
    
    estudiante = Estudiante(
        nombre='Estudiante Test',
        codigo='EST001',
        email='test@estudiante.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8')
    )
    db.session.add(estudiante)
    db.session.commit()
    return estudiante


@pytest.fixture
def sesion_test(app, estudiante_test, profesor_test):
    """Create a test session."""
    sesion = Sesion(
        estudiante_id=estudiante_test.id,
        profesor_id=profesor_test.id,
        maqueta='A/C',
        puntaje=4.5,
        tiempo_segundos=300,
        interacciones_ia=5
    )
    db.session.add(sesion)
    db.session.commit()
    return sesion
