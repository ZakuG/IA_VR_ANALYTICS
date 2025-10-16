"""
Script de migración para actualizar la base de datos
Agrega el campo nivel_habilidad y hace profesor_id nullable
"""

from app import app, db

def migrar_base_datos():
    """Actualiza la estructura de la base de datos"""
    
    with app.app_context():
        print("🔄 Migrando base de datos...")
        
        try:
            # Recrear todas las tablas con la nueva estructura
            print("⚠️  Recreando tablas (se perderán datos existentes)...")
            db.drop_all()
            db.create_all()
            print("✅ Base de datos actualizada exitosamente")
            print("\n📝 Cambios aplicados:")
            print("   - Campo 'nivel_habilidad' agregado a Estudiante (default: 3)")
            print("   - Campo 'profesor_id' ahora es opcional (nullable)")
            print("   - Formato de código cambiado a EST0001, EST0002, etc.")
            print("\n⚠️  IMPORTANTE: Ejecuta 'python generate_test_data.py' para crear datos de prueba")
            
        except Exception as e:
            print(f"❌ Error al migrar: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - Sistema VR Analytics")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Este script recreará la base de datos")
    print("⚠️  Se perderán todos los datos existentes")
    
    respuesta = input("\n¿Deseas continuar? (si/no): ").lower()
    
    if respuesta in ['si', 's', 'yes', 'y']:
        if migrar_base_datos():
            print("\n✅ Migración completada exitosamente")
            print("\nPróximos pasos:")
            print("1. Ejecuta: python generate_test_data.py")
            print("2. Ejecuta: python app.py")
            print("3. Registra nuevos estudiantes y verás el código generado automáticamente")
        else:
            print("\n❌ Migración fallida")
    else:
        print("\n❌ Migración cancelada")
