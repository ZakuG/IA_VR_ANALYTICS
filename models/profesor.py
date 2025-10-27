"""
models/profesor.py - Modelo de Profesor
"""

from flask_login import UserMixin
from models.base import db, bcrypt
from datetime import datetime


class Profesor(UserMixin, db.Model):
    """Modelo de Profesor con métodos helper"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    institucion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    
    # Relación many-to-many con estudiantes
    from models.base import estudiante_profesor
    estudiantes = db.relationship(
        'Estudiante', 
        secondary=estudiante_profesor, 
        backref=db.backref('profesores', lazy='dynamic'),
        lazy='dynamic'
    )
    
    def get_id(self):
        """Sobrescribe get_id para Flask-Login"""
        return f"profesor_{self.id}"
    
    def to_dict(self, include_estudiantes=False):
        """Serializa el profesor a diccionario"""
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'institucion': self.institucion,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
        
        if include_estudiantes:
            data['total_estudiantes'] = self.estudiantes.count()
            
        return data
    
    def set_password(self, password: str):
        """Establece la contraseña hasheada"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifica la contraseña"""
        return bcrypt.check_password_hash(self.password, password)
    
    @property
    def total_sesiones_evaluadas(self) -> int:
        """Número total de sesiones evaluadas por este profesor"""
        from models.sesion import Sesion
        return Sesion.query.filter_by(profesor_id=self.id).count()
    
    def __repr__(self):
        return f'<Profesor {self.nombre} ({self.email})>'
