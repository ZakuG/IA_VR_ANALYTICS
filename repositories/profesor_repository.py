"""
Profesor Repository - Gestión de profesores
Maneja todas las operaciones CRUD de profesores
"""

from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Profesor, Estudiante


class ProfesorRepository:
    """Repository para gestionar profesores"""
    
    @staticmethod
    def create(nombre: str, email: str, password: str, institucion: Optional[str] = None) -> Profesor:
        """
        Crea un nuevo profesor
        
        Args:
            nombre: Nombre del profesor
            email: Email único del profesor
            password: Contraseña
            institucion: Institución educativa (opcional)
            
        Returns:
            Profesor creado
            
        Raises:
            ValueError: Si el email ya existe
        """
        # Verificar si ya existe
        if ProfesorRepository.get_by_email(email):
            raise ValueError(f"Ya existe un profesor con email {email}")
        
        # Normalizar institución (evitar None o cadena vacía)
        if not institucion or institucion.strip() == '':
            institucion = "Sin institución"
        
        profesor = Profesor(
            nombre=nombre,
            email=email,
            institucion=institucion
        )
        profesor.set_password(password)
        
        db.session.add(profesor)
        db.session.commit()
        
        return profesor
    
    @staticmethod
    def get_by_id(profesor_id: int) -> Optional[Profesor]:
        """Obtiene un profesor por ID"""
        return Profesor.query.get(profesor_id)
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Profesor]:
        """Obtiene un profesor por email"""
        return Profesor.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all() -> List[Profesor]:
        """Obtiene todos los profesores"""
        return Profesor.query.order_by(Profesor.nombre).all()
    
    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Profesor]:
        """
        Autentica un profesor
        
        Args:
            email: Email del profesor
            password: Contraseña
            
        Returns:
            Profesor si las credenciales son correctas, None en caso contrario
        """
        profesor = ProfesorRepository.get_by_email(email)
        
        if profesor and profesor.check_password(password):
            return profesor
        
        return None
    
    @staticmethod
    def get_estudiantes(profesor_id: int) -> List[Estudiante]:
        """
        Obtiene los estudiantes inscritos con un profesor
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            Lista de estudiantes
        """
        profesor = ProfesorRepository.get_by_id(profesor_id)
        
        if not profesor:
            return []
        
        return profesor.estudiantes
    
    @staticmethod
    def update_password(profesor_id: int, new_password: str) -> bool:
        """
        Actualiza la contraseña de un profesor
        
        Args:
            profesor_id: ID del profesor
            new_password: Nueva contraseña
            
        Returns:
            True si se actualizó correctamente
        """
        profesor = ProfesorRepository.get_by_id(profesor_id)
        
        if not profesor:
            return False
        
        profesor.set_password(new_password)
        db.session.commit()
        
        return True
    
    @staticmethod
    def delete(profesor_id: int) -> bool:
        """
        Elimina un profesor
        
        Args:
            profesor_id: ID del profesor
            
        Returns:
            True si se eliminó, False si no existía
        """
        profesor = ProfesorRepository.get_by_id(profesor_id)
        
        if not profesor:
            return False
        
        db.session.delete(profesor)
        db.session.commit()
        
        return True
