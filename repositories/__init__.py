"""
Repositorios - Capa de acceso a datos
Patrón Repository para abstraer la lógica de acceso a la base de datos
"""

from .session_repository import SessionRepository
from .estudiante_repository import EstudianteRepository
from .profesor_repository import ProfesorRepository

__all__ = [
    'SessionRepository',
    'EstudianteRepository',
    'ProfesorRepository'
]
