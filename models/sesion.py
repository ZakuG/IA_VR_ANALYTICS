"""
models/sesion.py - Modelo de Sesión VR
"""

from models.base import db
from datetime import datetime
import json


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
        """Indica si la sesión está aprobada (puntaje >= 4)"""
        return self.puntaje >= 4
    
    @property
    def tiempo_minutos(self) -> float:
        """Tiempo en minutos"""
        return round(self.tiempo_segundos / 60, 2)
    
    @property
    def calificacion(self) -> str:
        """Calificación textual basada en puntaje (escala 0-7)"""
        if self.puntaje >= 6.5:
            return "Excelente"
        elif self.puntaje >= 5.5:
            return "Muy Bueno"
        elif self.puntaje >= 4.5:
            return "Bueno"
        elif self.puntaje >= 4.0:
            return "Regular"
        else:
            return "Insuficiente"
    
    @property
    def eficiencia(self) -> str:
        """Eficiencia basada en tiempo y puntaje"""
        if self.puntaje >= 5.5 and self.tiempo_segundos < 300:
            return "Alta"
        elif self.puntaje >= 4 and self.tiempo_segundos < 600:
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
        return f'<Sesion {self.id}: {self.estudiante.nombre if self.estudiante else "N/A"} - {self.maqueta} ({self.puntaje}/7.0)>'
