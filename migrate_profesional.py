"""
Script de migración para actualizar el sistema a versión profesional
- Tabla relacional Estudiante-Profesor (many-to-many)
- Sesiones vinculadas a profesor específico
- Preserva datos existentes
"""

from app import app, db, Profesor, Estudiante, Sesion
from datetime import datetime
import json
import shutil
import os

def migrar_base_datos():
    """
    Migración profesional de la base de datos
    """
    with app.app_context():
        print("🔄 Iniciando migración de base de datos...")
        
        # Hacer backup de la base de datos
        db_path = os.path.join('instance', 'database.db')
        if os.path.exists(db_path):
            backup_path = db_path + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backup creado: {backup_path}")
        
        # Guardar datos existentes
        print("📊 Guardando datos existentes...")
        profesores_data = []
        estudiantes_data = []
        sesiones_data = []
        
        try:
            for p in Profesor.query.all():
                profesores_data.append({
                    'id': p.id,
                    'nombre': p.nombre,
                    'email': p.email,
                    'password': p.password,
                    'institucion': p.institucion
                })
            
            for e in Estudiante.query.all():
                estudiantes_data.append({
                    'id': e.id,
                    'nombre': e.nombre,
                    'codigo': e.codigo,
                    'email': e.email,
                    'password': e.password,
                    'profesor_id': e.profesor_id,
                    'nivel_habilidad': e.nivel_habilidad
                })
            
            for s in Sesion.query.all():
                sesiones_data.append({
                    'id': s.id,
                    'estudiante_id': s.estudiante_id,
                    'maqueta': s.maqueta,
                    'tiempo_segundos': s.tiempo_segundos,
                    'puntaje': s.puntaje,
                    'fecha': s.fecha,
                    'respuestas_detalle': s.respuestas_detalle,
                    'interacciones_ia': s.interacciones_ia,
                    'profesor_id': getattr(s, 'profesor_id', None)  # Si ya existe
                })
            
            print(f"✅ Guardados: {len(profesores_data)} profesores, {len(estudiantes_data)} estudiantes, {len(sesiones_data)} sesiones")
            
        except Exception as e:
            print(f"⚠️ No hay datos previos: {e}")
        
        # Recrear tablas
        print("🗑️ Eliminando tablas antiguas...")
        db.drop_all()
        
        print("🔨 Creando nuevas tablas...")
        db.create_all()
        
        # Restaurar datos
        print("📥 Restaurando datos...")
        
        # Restaurar profesores
        for p_data in profesores_data:
            profesor = Profesor(
                nombre=p_data['nombre'],
                email=p_data['email'],
                password=p_data['password'],
                institucion=p_data['institucion']
            )
            db.session.add(profesor)
        
        db.session.commit()
        print(f"✅ Restaurados {len(profesores_data)} profesores")
        
        # Restaurar estudiantes
        estudiantes_map = {}
        profesor_id_map = {}  # Para rastrear qué profesor tenía cada estudiante
        
        for e_data in estudiantes_data:
            estudiante = Estudiante(
                nombre=e_data['nombre'],
                codigo=e_data['codigo'],
                email=e_data['email'],
                password=e_data['password'],
                nivel_habilidad=e_data.get('nivel_habilidad', 3)
            )
            db.session.add(estudiante)
            db.session.flush()
            estudiantes_map[e_data['id']] = estudiante.id
            
            # Si tenía profesor asignado, crear relación
            if e_data.get('profesor_id'):
                profesor_id_map[estudiante.id] = e_data['profesor_id']
                profesor = Profesor.query.get(e_data['profesor_id'])
                if profesor and estudiante not in profesor.estudiantes:
                    profesor.estudiantes.append(estudiante)
        
        db.session.commit()
        print(f"✅ Restaurados {len(estudiantes_data)} estudiantes con relaciones")
        
        # Restaurar sesiones
        for s_data in sesiones_data:
            nuevo_est_id = estudiantes_map.get(s_data['estudiante_id'], s_data['estudiante_id'])
            
            # Asignar profesor_id: usar el de la sesión si existe, sino el del estudiante
            profesor_id = s_data.get('profesor_id') or profesor_id_map.get(nuevo_est_id)
            
            sesion = Sesion(
                estudiante_id=nuevo_est_id,
                profesor_id=profesor_id,  # Ahora todas las sesiones tienen profesor
                maqueta=s_data['maqueta'],
                tiempo_segundos=s_data['tiempo_segundos'],
                puntaje=s_data['puntaje'],
                fecha=s_data['fecha'],
                respuestas_detalle=s_data['respuestas_detalle'],
                interacciones_ia=s_data['interacciones_ia']
            )
            db.session.add(sesion)
        
        db.session.commit()
        print(f"✅ Restauradas {len(sesiones_data)} sesiones")
        
        print("\n✨ ¡Migración completada exitosamente!")
        print("📊 Resumen:")
        print(f"   - Profesores: {Profesor.query.count()}")
        print(f"   - Estudiantes: {Estudiante.query.count()}")
        print(f"   - Sesiones: {Sesion.query.count()}")
        print("   - Tabla estudiante_profesor: Creada ✅")

if __name__ == '__main__':
    respuesta = input("⚠️ Esta operación modificará la base de datos. ¿Continuar? (si/no): ")
    if respuesta.lower() == 'si':
        migrar_base_datos()
    else:
        print("❌ Migración cancelada")
