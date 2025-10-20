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
            "Lucía Ramírez", "Nicolás Silva", "Emma Flores", "Julián Gómez" ,
            "Olivia Jiménez", "Gabriel Cruz", "Victoria Ortiz",
            "Daniela Moreno", "Alejandro Sánchez", "Mía Torres",
            "Joaquín Pérez",
            "Samuel Ruiz", "Paula Jiménez", "Adrián Flores",
            "Natalia Gómez", "Bruno Díaz", "Sara Torres",
            "Emilia Vargas", "Tomás Fernández", "Renata Silva",
            "Diego Morales", "Camila Jiménez", "Matías Ruiz"
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
        
        # Dividir estudiantes en 3 grupos equitativos
        total_estudiantes = len(estudiantes)
        tercio = total_estudiantes // 3
        
        # Grupo 1: Estudiantes que reprueban (0 a 3.9) - primer tercio
        estudiantes_bajo = estudiantes[:tercio]
        
        # Grupo 2: Estudiantes intermedios (4 a 5.5) - segundo tercio
        estudiantes_medio = estudiantes[tercio:tercio*2]
        
        # Grupo 3: Estudiantes buenos (5.5 a 7) - último tercio
        estudiantes_alto = estudiantes[tercio*2:]
        
        print(f"📊 Distribución de estudiantes:")
        print(f"   🔴 Bajo rendimiento (0-3.9): {len(estudiantes_bajo)} estudiantes")
        print(f"   🟡 Rendimiento medio (4-5.5): {len(estudiantes_medio)} estudiantes")
        print(f"   🟢 Alto rendimiento (5.5-7): {len(estudiantes_alto)} estudiantes")
        
        # Generar sesiones con datos realistas
        sesiones_generadas = 0
        
        # Función para generar sesión según grupo
        def generar_sesion(estudiante, grupo_rendimiento):
            """
            grupo_rendimiento: 'bajo' (0-3.9), 'medio' (4-5.5), 'alto' (5.5-7)
            """
            maqueta = random.choice(maquetas)
            
            if grupo_rendimiento == 'bajo':
                # Reprueban: puntaje 0 a 3.9
                puntaje_base = random.uniform(0, 3.9)
                tiempo_base = random.uniform(90, 120)  # Más lentos
                ia_base = random.uniform(8, 15)  # Usan mucho la IA
                
            elif grupo_rendimiento == 'medio':
                # Intermedios: puntaje 4 a 5.5
                puntaje_base = random.uniform(4.0, 5.5)
                tiempo_base = random.uniform(60, 90)  # Tiempo medio
                ia_base = random.uniform(3, 8)  # Uso moderado de IA
                
            else:  # 'alto'
                # Buenos: puntaje 5.5 a 7
                puntaje_base = random.uniform(5.5, 7.0)
                tiempo_base = random.uniform(30, 60)  # Rápidos
                ia_base = random.uniform(0, 3)  # Poco uso de IA
            
            # Agregar variación realista
            puntaje = int(round(max(0, min(7, random.gauss(puntaje_base, 0.5)))))
            tiempo_segundos = int(max(30, min(120, random.gauss(tiempo_base, 10))))
            interacciones_ia = int(max(0, random.gauss(ia_base, 2)))
            
            # Fecha: últimos 30 días
            fecha = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            
            return Sesion(
                estudiante_id=estudiante.id,
                profesor_id=profesor.id,
                maqueta=maqueta,
                tiempo_segundos=tiempo_segundos,
                puntaje=puntaje,
                fecha=fecha,
                interacciones_ia=interacciones_ia,
                respuestas_detalle='{"respuestas": []}'
            )
        
        # Generar sesiones para cada grupo
        for estudiante in estudiantes_bajo:
            num_sesiones = random.randint(3, 12)
            for _ in range(num_sesiones):
                sesion = generar_sesion(estudiante, 'bajo')
                db.session.add(sesion)
                sesiones_generadas += 1
        
        for estudiante in estudiantes_medio:
            num_sesiones = random.randint(3, 12)
            for _ in range(num_sesiones):
                sesion = generar_sesion(estudiante, 'medio')
                db.session.add(sesion)
                sesiones_generadas += 1
        
        for estudiante in estudiantes_alto:
            num_sesiones = random.randint(3, 12)
            for _ in range(num_sesiones):
                sesion = generar_sesion(estudiante, 'alto')
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
