"""
models/estudiante.py - Modelo de Estudiante
"""

from flask_login import UserMixin
from models.base import db, bcrypt
from datetime import datetime


class Estudiante(UserMixin, db.Model):
    """Modelo de Estudiante con métodos helper"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    nivel_habilidad = db.Column(db.Integer, default=4)  # 1-5, default 4 (intermedio)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    
    # Relación con sesiones
    sesiones = db.relationship('Sesion', backref='estudiante', lazy=True)
    # Nota: profesores es una relación many-to-many definida en Profesor
    
    def get_id(self):
        """Sobrescribe get_id para Flask-Login"""
        return f"estudiante_{self.id}"
    
    def to_dict(self, include_stats=False):
        """Serializa el estudiante a diccionario"""
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'email': self.email,
            'nivel_habilidad': self.nivel_habilidad,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
        
        if include_stats:
            data['total_sesiones'] = len(self.sesiones)
            data['total_profesores'] = self.profesores.count()
            
            if self.sesiones:
                puntajes = [s.puntaje for s in self.sesiones]
                data['promedio_puntaje'] = round(sum(puntajes) / len(puntajes), 2)
            else:
                data['promedio_puntaje'] = 0
                
        return data
    
    def set_password(self, password: str):
        """Establece la contraseña hasheada"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifica la contraseña"""
        if not self.password:
            return False
        return bcrypt.check_password_hash(self.password, password)
    
    @property
    def promedio_puntaje(self) -> float:
        """Promedio de puntajes de todas las sesiones"""
        if not self.sesiones:
            return 0.0
        return round(sum(s.puntaje for s in self.sesiones) / len(self.sesiones), 2)
    
    @property
    def nivel_experiencia(self) -> str:
        """Nivel de experiencia basado en sesiones completadas"""
        total = len(self.sesiones)
        if total == 0:
            return "Novato"
        elif total < 5:
            return "Principiante"
        elif total < 15:
            return "Intermedio"
        elif total < 30:
            return "Avanzado"
        else:
            return "Experto"
    
    def __repr__(self):
        return f'<Estudiante {self.nombre} ({self.codigo})>'
