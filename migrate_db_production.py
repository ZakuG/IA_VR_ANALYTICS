#!/usr/bin/env python
"""
Script de migración para crear tablas en la base de datos
Ejecutar manualmente: python migrate_db.py
"""
import os
from app import app, db

def run_migration():
    """Ejecuta la migración de base de datos"""
    print("🔄 Iniciando migración de base de datos...")
    
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar tablas creadas
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📋 Tablas en la base de datos ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
                
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            raise

if __name__ == '__main__':
    run_migration()
