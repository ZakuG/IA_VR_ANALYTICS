"""
Auth Service - Servicio de autenticación
Maneja login, registro y gestión de sesiones
"""

from typing import Dict, Optional, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.estudiante_repository import EstudianteRepository
from repositories.profesor_repository import ProfesorRepository


class AuthService:
    """Servicio de autenticación y autorización"""
    
    def __init__(self):
        """Inicializa el servicio de autenticación"""
        self.estudiante_repo = EstudianteRepository()
        self.profesor_repo = ProfesorRepository()
    
    def login_estudiante(self, codigo: str, password: str) -> Dict[str, Any]:
        """
        Autentica un estudiante
        
        Args:
            codigo: Código del estudiante
            password: Contraseña
            
        Returns:
            Diccionario con resultado del login
        """
        estudiante = self.estudiante_repo.authenticate(codigo, password)
        
        if not estudiante:
            return {
                'success': False,
                'message': 'Código o contraseña incorrectos'
            }
        
        return {
            'success': True,
            'user_type': 'estudiante',
            'user': {
                'id': estudiante.id,
                'nombre': estudiante.nombre,
                'codigo': estudiante.codigo
            }
        }
    
    def login_profesor(self, email: str, password: str) -> Dict[str, Any]:
        """
        Autentica un profesor
        
        Args:
            email: Email del profesor
            password: Contraseña
            
        Returns:
            Diccionario con resultado del login
        """
        profesor = self.profesor_repo.authenticate(email, password)
        
        if not profesor:
            return {
                'success': False,
                'message': 'Email o contraseña incorrectos'
            }
        
        return {
            'success': True,
            'user_type': 'profesor',
            'user': {
                'id': profesor.id,
                'nombre': profesor.nombre,
                'email': profesor.email
            }
        }
    
    def register_estudiante(self, nombre: str, codigo: str, 
                           password: str, confirm_password: str,
                           email: Optional[str] = None) -> Dict[str, Any]:
        """
        Registra un nuevo estudiante
        
        Args:
            nombre: Nombre completo
            codigo: Código único
            password: Contraseña
            confirm_password: Confirmación de contraseña
            email: Email del estudiante (opcional)
            
        Returns:
            Diccionario con resultado del registro
        """
        # Validaciones
        if not all([nombre, codigo, password, confirm_password]):
            return {
                'success': False,
                'message': 'Todos los campos son requeridos'
            }
        
        if password != confirm_password:
            return {
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }
        
        if len(password) < 4:
            return {
                'success': False,
                'message': 'La contraseña debe tener al menos 4 caracteres'
            }
        
        try:
            estudiante = self.estudiante_repo.create(nombre, codigo, password, email)
            
            return {
                'success': True,
                'message': 'Estudiante registrado correctamente',
                'user': {
                    'id': estudiante.id,
                    'nombre': estudiante.nombre,
                    'codigo': estudiante.codigo
                }
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al registrar: {str(e)}'
            }
    
    def register_profesor(self, nombre: str, email: str, 
                         password: str, confirm_password: str) -> Dict[str, Any]:
        """
        Registra un nuevo profesor
        
        Args:
            nombre: Nombre completo
            email: Email único
            password: Contraseña
            confirm_password: Confirmación de contraseña
            
        Returns:
            Diccionario con resultado del registro
        """
        # Validaciones
        if not all([nombre, email, password, confirm_password]):
            return {
                'success': False,
                'message': 'Todos los campos son requeridos'
            }
        
        if password != confirm_password:
            return {
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }
        
        if len(password) < 4:
            return {
                'success': False,
                'message': 'La contraseña debe tener al menos 4 caracteres'
            }
        
        if '@' not in email:
            return {
                'success': False,
                'message': 'Email inválido'
            }
        
        try:
            profesor = self.profesor_repo.create(nombre, email, password)
            
            return {
                'success': True,
                'message': 'Profesor registrado correctamente',
                'user': {
                    'id': profesor.id,
                    'nombre': profesor.nombre,
                    'email': profesor.email
                }
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al registrar: {str(e)}'
            }
    
    def inscribir_estudiante_profesor(self, estudiante_id: int, 
                                      profesor_id: int) -> Dict[str, Any]:
        """
        Inscribe a un estudiante con un profesor
        
        Args:
            estudiante_id: ID del estudiante
            profesor_id: ID del profesor
            
        Returns:
            Diccionario con resultado
        """
        try:
            ya_inscrito = not self.estudiante_repo.inscribir_profesor(
                estudiante_id, profesor_id
            )
            
            return {
                'success': True,
                'ya_inscrito': ya_inscrito,
                'message': 'Ya estabas inscrito' if ya_inscrito else 'Inscripción exitosa'
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al inscribir: {str(e)}'
            }
    
    def get_profesores_disponibles(self) -> list:
        """
        Obtiene lista de todos los profesores disponibles
        
        Returns:
            Lista de profesores serializados
        """
        profesores = self.profesor_repo.get_all()
        
        return [{
            'id': p.id,
            'nombre': p.nombre,
            'email': p.email,
            'institucion': p.institucion,
            'total_estudiantes': p.estudiantes.count()  # Usar .count() en lugar de len()
        } for p in profesores]
