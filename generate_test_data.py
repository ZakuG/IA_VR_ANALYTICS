# generate_test_data.py
"""
Script para generar datos de prueba para el sistema VR Analytics
"""

from app import app, db, Profesor, Estudiante, Sesion
from flask_bcrypt import Bcrypt
import random
from datetime import datetime, timedelta

bcrypt = Bcrypt()

def generar_datos_prueba():
    """Genera datos de prueba para demostración"""
    
    with app.app_context():
        # Limpiar base de datos
        print("Limpiando base de datos...")
        db.drop_all()
        db.create_all()
        
        # Crear profesor de prueba
        print("Creando profesor de prueba...")
        profesor = Profesor(
            nombre="Dr. Juan Pérez",
            email="profesor@test.com",
            password=bcrypt.generate_password_hash("123456").decode('utf-8'),
            institucion="Universidad San Sebastian"
        )
        db.session.add(profesor)
        db.session.commit()
        
        # Crear estudiantes
        print("Creando estudiantes...")
        nombres_estudiantes = [
            "María González", "Carlos Rodríguez", "Ana Martínez", 
            "Luis Fernández", "Sofia López", "Diego Torres",
            "Valentina Castro", "Sebastián Rojas", "Camila Vargas",
            "Mateo Herrera", "Isabella Morales", "Santiago Díaz",
            "Lucía Ramírez", "Nicolás Silva", "Emma Flores"
        ]
        
        estudiantes = []
        for i, nombre in enumerate(nombres_estudiantes, 1):
            estudiante = Estudiante(
                nombre=nombre,
                codigo=f"EST{i:04d}",  # Formato EST0001
                email=f"estudiante{i}@test.com",
                password=bcrypt.generate_password_hash("123456").decode('utf-8'),
                nivel_habilidad=random.randint(2, 5)  # Nivel entre 2 y 5
            )
            estudiantes.append(estudiante)
            db.session.add(estudiante)
            db.session.flush()  # Para obtener el ID
            
            # Crear relación con el profesor (many-to-many)
            profesor.estudiantes.append(estudiante)
        
        db.session.commit()
        
        # Crear sesiones de prueba
        print("Creando sesiones de prueba...")
        maquetas = ["Aire acondicionado", "Motor"]
        
        # Generar sesiones con datos realistas
        sesiones_generadas = 0
        
        for estudiante in estudiantes:
            # Cada estudiante tiene entre 3 y 8 sesiones
            num_sesiones = random.randint(3, 8)
            
            for j in range(num_sesiones):
                # Seleccionar maqueta aleatoria
                maqueta = random.choice(maquetas)
                
                # Generar datos correlacionados (estudiantes buenos -> menos tiempo, más puntaje)
                nivel_estudiante = random.uniform(0, 1)  # 0 = bajo, 1 = alto
                
                # Tiempo: estudiantes mejores son más rápidos (30-120 segundos)
                tiempo_base = 120 - (nivel_estudiante * 60)
                tiempo_segundos = int(max(30, min(120, random.gauss(tiempo_base, 20))))
                
                # Puntaje: correlacionado con nivel del estudiante
                puntaje_esperado = nivel_estudiante * 5
                puntaje = int(max(0, min(5, random.gauss(puntaje_esperado, 1))))
                
                # Interacciones IA: estudiantes con dificultad usan más la IA
                ia_base = (1 - nivel_estudiante) * 10
                interacciones_ia = int(max(0, random.gauss(ia_base, 3)))
                
                # Fecha: últimos 30 días
                fecha = datetime.utcnow() - timedelta(days=random.randint(0, 30))
                
                sesion = Sesion(
                    estudiante_id=estudiante.id,
                    profesor_id=profesor.id,  # Marcar que el profesor registró esta sesión
                    maqueta=maqueta,
                    tiempo_segundos=tiempo_segundos,
                    puntaje=puntaje,
                    fecha=fecha,
                    interacciones_ia=interacciones_ia,
                    respuestas_detalle='{"respuestas": []}'
                )
                
                db.session.add(sesion)
                sesiones_generadas += 1
        
        db.session.commit()
        
        print(f"\n✅ Datos de prueba generados exitosamente!")
        print(f"   - 1 Profesor creado")
        print(f"   - {len(estudiantes)} Estudiantes creados")
        print(f"   - {sesiones_generadas} Sesiones creadas")
        print(f"\nCredenciales de prueba:")
        print(f"   Email: profesor@test.com")
        print(f"   Password: 123456")

if __name__ == '__main__':
    generar_datos_prueba()
