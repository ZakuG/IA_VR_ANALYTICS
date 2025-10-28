"""
Script para agregar índices a la base de datos PostgreSQL
Esto mejorará significativamente la velocidad de las consultas
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Sesion, Estudiante, Profesor
from sqlalchemy import text

def create_indexes():
    """Crea índices para optimizar consultas frecuentes"""
    
    with app.app_context():
        print("🔍 Creando índices en PostgreSQL...")
        
        try:
            # Índice en sesion.profesor_id (query más frecuente)
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sesion_profesor_id 
                ON sesion(profesor_id);
            """))
            print("✅ Índice creado: idx_sesion_profesor_id")
            
            # Índice en sesion.estudiante_id
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sesion_estudiante_id 
                ON sesion(estudiante_id);
            """))
            print("✅ Índice creado: idx_sesion_estudiante_id")
            
            # Índice en sesion.fecha (para ordenamiento)
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sesion_fecha 
                ON sesion(fecha DESC);
            """))
            print("✅ Índice creado: idx_sesion_fecha")
            
            # Índice compuesto para consultas de estudiante por profesor
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sesion_profesor_estudiante 
                ON sesion(profesor_id, estudiante_id);
            """))
            print("✅ Índice creado: idx_sesion_profesor_estudiante")
            
            # Índice en maqueta para filtros
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sesion_maqueta 
                ON sesion(maqueta);
            """))
            print("✅ Índice creado: idx_sesion_maqueta")
            
            # Commit todos los índices
            db.session.commit()
            print("\n✅ Todos los índices creados exitosamente!")
            print("\n📊 Verificando índices...")
            
            # Listar todos los índices de la tabla sesion
            result = db.session.execute(text("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'sesion'
                ORDER BY indexname;
            """))
            
            print("\n🔍 Índices en tabla 'sesion':")
            for row in result:
                print(f"  - {row[0]}")
            
            print("\n🚀 Base de datos optimizada para queries rápidas!")
            
        except Exception as e:
            print(f"❌ Error al crear índices: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_indexes()
