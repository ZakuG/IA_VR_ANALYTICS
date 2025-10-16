"""
Script para agregar un segundo profesor y algunos estudiantes compartidos
"""

from app import app, db, Profesor, Estudiante, Sesion
from flask_bcrypt import Bcrypt
import random
from datetime import datetime, timedelta

bcrypt = Bcrypt()

def agregar_segundo_profesor():
    """Agrega un segundo profesor y lo vincula con algunos estudiantes existentes"""
    
    with app.app_context():
        # Crear segundo profesor
        print("Creando segundo profesor...")
        profesor2 = Profesor(
            nombre="Dra. María López",
            email="profesora@test.com",
            password=bcrypt.generate_password_hash("123456").decode('utf-8'),
            institucion="Universidad San Sebastian"
        )
        db.session.add(profesor2)
        db.session.commit()
        
        # Obtener algunos estudiantes existentes (primeros 5)
        estudiantes = Estudiante.query.limit(5).all()
        
        print(f"Inscribiendo {len(estudiantes)} estudiantes con el segundo profesor...")
        
        # Inscribir estudiantes con el segundo profesor
        for estudiante in estudiantes:
            if profesor2 not in estudiante.profesores:
                profesor2.estudiantes.append(estudiante)
        
        db.session.commit()
        
        # Crear algunas sesiones registradas por el segundo profesor
        print("Creando sesiones para el segundo profesor...")
        maquetas = ["Aire acondicionado", "Motor"]
        sesiones_generadas = 0
        
        for estudiante in estudiantes:
            # 2-4 sesiones por estudiante con este profesor
            num_sesiones = random.randint(2, 4)
            
            for _ in range(num_sesiones):
                maqueta = random.choice(maquetas)
                nivel_estudiante = random.uniform(0, 1)
                
                tiempo_base = 120 - (nivel_estudiante * 60)
                tiempo_segundos = int(max(30, min(120, random.gauss(tiempo_base, 20))))
                
                puntaje_esperado = nivel_estudiante * 5
                puntaje = int(max(0, min(5, random.gauss(puntaje_esperado, 1))))
                
                ia_base = (1 - nivel_estudiante) * 10
                interacciones_ia = int(max(0, random.gauss(ia_base, 3)))
                
                fecha = datetime.utcnow() - timedelta(days=random.randint(0, 15))
                
                sesion = Sesion(
                    estudiante_id=estudiante.id,
                    profesor_id=profesor2.id,  # Sesión del segundo profesor
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
        
        print(f"\n✅ Segundo profesor agregado exitosamente!")
        print(f"   - Profesora: Dra. María López")
        print(f"   - {len(estudiantes)} Estudiantes compartidos")
        print(f"   - {sesiones_generadas} Sesiones nuevas creadas")
        print(f"\nCredenciales:")
        print(f"   Email: profesora@test.com")
        print(f"   Password: 123456")
        print(f"\nEstudiantes compartidos ahora tienen 2 profesores y pueden filtrar por cada uno.")

if __name__ == '__main__':
    agregar_segundo_profesor()
