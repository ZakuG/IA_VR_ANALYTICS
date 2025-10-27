"""
Script para verificar profesores
"""

from app import app
from services.auth_service import AuthService

def verificar_profesores():
    """Verifica que los profesores tengan institución"""
    with app.app_context():
        auth = AuthService()
        profesores = auth.get_profesores_disponibles()
        
        print("\n📚 LISTA DE PROFESORES:")
        print("=" * 80)
        
        for p in profesores:
            institucion = p.get('institucion') or 'Sin institucion'
            print(f"\n👤 {p['nombre']}")
            print(f"   📧 Email: {p['email']}")
            print(f"   🏫 Institucion: {institucion}")
            print(f"   👥 Estudiantes: {p['total_estudiantes']}")
        
        print("\n" + "=" * 80)
        print(f"Total: {len(profesores)} profesores")

if __name__ == '__main__':
    verificar_profesores()
