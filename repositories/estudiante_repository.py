"""
Estudiante Repository - Gestión de estudiantes
Maneja todas las operaciones CRUD de estudiantes
"""

from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Estudiante, Profesor


class EstudianteRepository:
    """Repository para gestionar estudiantes"""
    
    @staticmethod
    def create(nombre: str, codigo: str, password: str, email: Optional[str] = None) -> Estudiante:
        """
        Crea un nuevo estudiante
        
        Args:
            nombre: Nombre del estudiante
            codigo: Código único del estudiante
            password: Contraseña
            email: Email del estudiante (opcional)
            
        Returns:
            Estudiante creado
            
        Raises:
            ValueError: Si el código ya existe
        """
        # Verificar si ya existe
        if EstudianteRepository.get_by_codigo(codigo):
            raise ValueError(f"Ya existe un estudiante con código {codigo}")
        
        estudiante = Estudiante(
            nombre=nombre,
            codigo=codigo,
            email=email  # Agregar email si viene
        )
        estudiante.set_password(password)
        
        db.session.add(estudiante)
        db.session.commit()
        
        return estudiante
    
    @staticmethod
    def get_by_id(estudiante_id: int) -> Optional[Estudiante]:
        """Obtiene un estudiante por ID"""
        return Estudiante.query.get(estudiante_id)
    
    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Estudiante]:
        """Obtiene un estudiante por código"""
        return Estudiante.query.filter_by(codigo=codigo).first()
    
    @staticmethod
    def get_all() -> List[Estudiante]:
        """Obtiene todos los estudiantes"""
        return Estudiante.query.order_by(Estudiante.nombre).all()
    
    @staticmethod
    def authenticate(codigo: str, password: str) -> Optional[Estudiante]:
        """
        Autentica un estudiante
        
        Args:
            codigo: Código del estudiante
            password: Contraseña
            
        Returns:
            Estudiante si las credenciales son correctas, None en caso contrario
        """
        estudiante = EstudianteRepository.get_by_codigo(codigo)
        
        if estudiante and estudiante.check_password(password):
            return estudiante
        
        return None
    
    @staticmethod
    def inscribir_profesor(estudiante_id: int, profesor_id: int) -> bool:
        """
        Inscribe a un estudiante con un profesor
        
        Args:
            estudiante_id: ID del estudiante
            profesor_id: ID del profesor
            
        Returns:
            True si se inscribió, False si ya estaba inscrito
            
        Raises:
            ValueError: Si el estudiante o profesor no existen
        """
        estudiante = EstudianteRepository.get_by_id(estudiante_id)
        if not estudiante:
            raise ValueError(f"Estudiante {estudiante_id} no encontrado")
        
        from repositories.profesor_repository import ProfesorRepository
        profesor = ProfesorRepository.get_by_id(profesor_id)
        if not profesor:
            raise ValueError(f"Profesor {profesor_id} no encontrado")
        
        # Verificar si ya está inscrito
        if profesor in estudiante.profesores:
            return False
        
        estudiante.profesores.append(profesor)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_profesores(estudiante_id: int) -> List[Profesor]:
        """
        Obtiene los profesores de un estudiante
        
        Args:
            estudiante_id: ID del estudiante
            
        Returns:
            Lista de profesores
        """
        estudiante = EstudianteRepository.get_by_id(estudiante_id)
        
        if not estudiante:
            return []
        
        return estudiante.profesores
    
    @staticmethod
    def update_password(estudiante_id: int, new_password: str) -> bool:
        """
        Actualiza la contraseña de un estudiante
        
        Args:
            estudiante_id: ID del estudiante
            new_password: Nueva contraseña
            
        Returns:
            True si se actualizó correctamente
        """
        estudiante = EstudianteRepository.get_by_id(estudiante_id)
        
        if not estudiante:
            return False
        
        estudiante.set_password(new_password)
        db.session.commit()
        
        return True
    
    @staticmethod
    def delete(estudiante_id: int) -> bool:
        """
        Elimina un estudiante
        
        Args:
            estudiante_id: ID del estudiante
            
        Returns:
            True si se eliminó, False si no existía
        """
        estudiante = EstudianteRepository.get_by_id(estudiante_id)
        
        if not estudiante:
            return False
        
        db.session.delete(estudiante)
        db.session.commit()
        
        return True
