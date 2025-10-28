"""
Script para agregar un segundo profesor y algunos estudiantes compartidos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Profesor, Estudiante, Sesion
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
        estudiantes = Estudiante.query.limit(15).all()
        
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
        
        # Dividir estudiantes en 3 grupos para variedad
        tercio = len(estudiantes) // 3
        estudiantes_bajo = estudiantes[:tercio]
        estudiantes_medio = estudiantes[tercio:tercio*2]
        estudiantes_alto = estudiantes[tercio*2:]
        
        def generar_sesion_profesor2(estudiante, grupo_rendimiento):
            """Genera sesión con rendimiento según grupo"""
            maqueta = random.choice(maquetas)
            
            if grupo_rendimiento == 'bajo':
                puntaje_base = random.uniform(0, 3.9)
                tiempo_base = random.uniform(90, 120)
                ia_base = random.uniform(8, 15)
            elif grupo_rendimiento == 'medio':
                puntaje_base = random.uniform(4.0, 5.5)
                tiempo_base = random.uniform(60, 90)
                ia_base = random.uniform(3, 8)
            else:  # 'alto'
                puntaje_base = random.uniform(5.5, 7.0)
                tiempo_base = random.uniform(30, 60)
                ia_base = random.uniform(0, 3)
            
            puntaje = int(round(max(0, min(7, random.gauss(puntaje_base, 0.5)))))
            tiempo_segundos = int(max(30, min(120, random.gauss(tiempo_base, 10))))
            interacciones_ia = int(max(0, random.gauss(ia_base, 2)))
            fecha = datetime.utcnow() - timedelta(days=random.randint(0, 15))
            
            return Sesion(
                estudiante_id=estudiante.id,
                profesor_id=profesor2.id,
                maqueta=maqueta,
                tiempo_segundos=tiempo_segundos,
                puntaje=puntaje,
                fecha=fecha,
                interacciones_ia=interacciones_ia,
                respuestas_detalle='{"respuestas": []}'
            )
        
        # Generar sesiones por grupo
        for estudiante in estudiantes_bajo:
            for _ in range(random.randint(2, 4)):
                db.session.add(generar_sesion_profesor2(estudiante, 'bajo'))
                sesiones_generadas += 1
        
        for estudiante in estudiantes_medio:
            for _ in range(random.randint(2, 4)):
                db.session.add(generar_sesion_profesor2(estudiante, 'medio'))
                sesiones_generadas += 1
        
        for estudiante in estudiantes_alto:
            for _ in range(random.randint(2, 4)):
                db.session.add(generar_sesion_profesor2(estudiante, 'alto'))
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
