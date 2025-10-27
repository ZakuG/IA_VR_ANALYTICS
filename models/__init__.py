"""
models/__init__.py - Punto de entrada del paquete models
Exporta todos los modelos y extensiones para compatibilidad con imports existentes
"""

# Importar extensiones base
from models.base import db, bcrypt, estudiante_profesor

# Importar modelos (IMPORTANTE: en orden de dependencias)
from models.profesor import Profesor
from models.estudiante import Estudiante
from models.sesion import Sesion

# Exportar todo para compatibilidad con imports existentes
# Permite hacer: from models import db, Profesor, Estudiante, Sesion
__all__ = [
    'db',
    'bcrypt',
    'estudiante_profesor',
    'Profesor',
    'Estudiante',
    'Sesion'
]
