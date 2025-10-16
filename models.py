"""
Models - Definición de modelos de base de datos
Separado de app.py para evitar imports circulares
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
import json

db = SQLAlchemy()
bcrypt = Bcrypt()

# Tabla de asociación para relación many-to-many entre Estudiante y Profesor
estudiante_profesor = db.Table('estudiante_profesor',
    db.Column('estudiante_id', db.Integer, db.ForeignKey('estudiante.id'), primary_key=True),
    db.Column('profesor_id', db.Integer, db.ForeignKey('profesor.id'), primary_key=True),
    db.Column('fecha_inscripcion', db.DateTime, default=datetime.utcnow)
)

# Modelos de Base de Datos
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
    estudiantes = db.relationship('Estudiante', secondary=estudiante_profesor, 
                                   backref=db.backref('profesores', lazy='dynamic'),
                                   lazy='dynamic')
    
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
        return Sesion.query.filter_by(profesor_id=self.id).count()
    
    def __repr__(self):
        return f'<Profesor {self.nombre} ({self.email})>'

class Estudiante(UserMixin, db.Model):
    """Modelo de Estudiante con métodos helper"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    nivel_habilidad = db.Column(db.Integer, default=3)  # 1-5, default 3 (intermedio)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    sesiones = db.relationship('Sesion', backref='estudiante', lazy=True)
    # Nota: profesores ahora es una relación many-to-many definida en Profesor
    
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

class Sesion(db.Model):
    """Modelo de Sesión VR con métodos helper"""
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'), nullable=True)  # Sesión vinculada a profesor
    maqueta = db.Column(db.String(100), nullable=False)
    tiempo_segundos = db.Column(db.Integer, nullable=False)
    puntaje = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    respuestas_detalle = db.Column(db.Text)  # JSON con respuestas
    interacciones_ia = db.Column(db.Integer, default=0)
    
    # Relación con profesor (lazy)
    profesor = db.relationship('Profesor', backref=db.backref('sesiones_evaluadas', lazy=True))
    
    def to_dict(self, include_estudiante=False, include_profesor=False):
        """Serializa la sesión a diccionario"""
        data = {
            'id': self.id,
            'maqueta': self.maqueta,
            'tiempo_segundos': self.tiempo_segundos,
            'tiempo_minutos': round(self.tiempo_segundos / 60, 2),
            'puntaje': self.puntaje,
            'interacciones_ia': self.interacciones_ia,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'aprobado': self.aprobado
        }
        
        if include_estudiante and self.estudiante:
            data['estudiante'] = {
                'id': self.estudiante.id,
                'nombre': self.estudiante.nombre,
                'codigo': self.estudiante.codigo
            }
        
        if include_profesor and self.profesor:
            data['profesor'] = {
                'id': self.profesor.id,
                'nombre': self.profesor.nombre
            }
            
        return data
    
    @property
    def aprobado(self) -> bool:
        """Indica si la sesión está aprobada (puntaje >= 3)"""
        return self.puntaje >= 3
    
    @property
    def tiempo_minutos(self) -> float:
        """Tiempo en minutos"""
        return round(self.tiempo_segundos / 60, 2)
    
    @property
    def calificacion(self) -> str:
        """Calificación textual basada en puntaje"""
        if self.puntaje >= 4.5:
            return "Excelente"
        elif self.puntaje >= 4.0:
            return "Muy Bueno"
        elif self.puntaje >= 3.0:
            return "Bueno"
        elif self.puntaje >= 2.0:
            return "Regular"
        else:
            return "Insuficiente"
    
    @property
    def eficiencia(self) -> str:
        """Eficiencia basada en tiempo y puntaje"""
        if self.puntaje >= 4 and self.tiempo_segundos < 300:
            return "Alta"
        elif self.puntaje >= 3 and self.tiempo_segundos < 600:
            return "Media"
        else:
            return "Baja"
    
    def get_respuestas(self) -> list:
        """Obtiene las respuestas parseadas desde JSON"""
        if not self.respuestas_detalle:
            return []
        try:
            return json.loads(self.respuestas_detalle)
        except:
            return []
    
    def set_respuestas(self, respuestas: list):
        """Establece las respuestas serializándolas a JSON"""
        self.respuestas_detalle = json.dumps(respuestas)
    
    def __repr__(self):
        return f'<Sesion {self.id}: {self.estudiante.nombre if self.estudiante else "N/A"} - {self.maqueta} ({self.puntaje}/5)>'
