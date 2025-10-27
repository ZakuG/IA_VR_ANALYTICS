"""
models/base.py - Configuración base de SQLAlchemy y Bcrypt
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Instancias de extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()

# Tabla de asociación para relación many-to-many entre Estudiante y Profesor
estudiante_profesor = db.Table(
    'estudiante_profesor',
    db.Column('estudiante_id', db.Integer, db.ForeignKey('estudiante.id'), primary_key=True),
    db.Column('profesor_id', db.Integer, db.ForeignKey('profesor.id'), primary_key=True),
    db.Column('fecha_inscripcion', db.DateTime, default=datetime.utcnow)
)
