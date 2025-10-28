#!/usr/bin/env python
"""
Script de inicialización para Render.com
Ejecuta migraciones y configuraciones necesarias antes de iniciar la app
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from sqlalchemy import inspect

def init_production_db():
    """Inicializa la base de datos en producción"""
    with app.app_context():
        # Verificar si las tablas ya existen
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if len(existing_tables) == 0:
            print("📊 No se encontraron tablas. Creando estructura de base de datos...")
            db.create_all()
            print(f"✅ Tablas creadas exitosamente: {inspector.get_table_names()}")
        else:
            print(f"✅ Base de datos ya inicializada. Tablas existentes: {existing_tables}")
        
        return True

if __name__ == '__main__':
    try:
        init_production_db()
        print("✅ Inicialización completada exitosamente")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
