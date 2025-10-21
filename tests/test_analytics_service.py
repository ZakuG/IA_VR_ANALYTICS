"""
Tests para AnalyticsService - Validar contratos de API antes y después del refactoring

Objetivo: Asegurar que el refactoring de Issue #3 no rompa funcionalidad existente
"""

import sys
import os
import pytest
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.analytics_service import AnalyticsService
from models import Profesor, Estudiante, Sesion, db


@pytest.fixture
def analytics_service(app):
    """Fixture del servicio de analytics"""
    with app.app_context():
        return AnalyticsService()


@pytest.fixture
def setup_test_data(app):
    """
    Crea datos de prueba realistas:
    - 1 profesor
    - 1 estudiante
    - 5 sesiones en 2 maquetas diferentes
    """
    with app.app_context():
        # Crear profesor
        profesor = Profesor(
            nombre="Dr. Test",
            email="test@universidad.edu",
            institucion="Universidad Test"
        )
        profesor.set_password("test123")
        db.session.add(profesor)
        db.session.commit()
        
        # Crear estudiante
        estudiante = Estudiante(
            nombre="Estudiante Test",
            codigo="TEST001",
            email="estudiante@test.com"
        )
        estudiante.set_password("test123")
        db.session.add(estudiante)
        db.session.commit()
        
        # Crear 5 sesiones con datos variados
        fechas_base = datetime.now() - timedelta(days=10)
        sesiones_data = [
            # Maqueta "Cardiaca" - 3 sesiones
            {'maqueta': 'Cardiaca', 'puntaje': 4.5, 'tiempo': 1800, 'interacciones': 15, 'dia': 0},
            {'maqueta': 'Cardiaca', 'puntaje': 3.8, 'tiempo': 2100, 'interacciones': 12, 'dia': 3},
            {'maqueta': 'Cardiaca', 'puntaje': 4.2, 'tiempo': 1950, 'interacciones': 18, 'dia': 7},
            # Maqueta "Respiratoria" - 2 sesiones
            {'maqueta': 'Respiratoria', 'puntaje': 3.5, 'tiempo': 2400, 'interacciones': 10, 'dia': 2},
            {'maqueta': 'Respiratoria', 'puntaje': 4.0, 'tiempo': 2200, 'interacciones': 14, 'dia': 5}
        ]
        
        for data in sesiones_data:
            sesion = Sesion(
                estudiante_id=estudiante.id,
                profesor_id=profesor.id,
                maqueta=data['maqueta'],
                puntaje=data['puntaje'],
                tiempo_segundos=data['tiempo'],
                interacciones_ia=data['interacciones'],
                fecha=fechas_base + timedelta(days=data['dia'])
            )
            db.session.add(sesion)
        
        db.session.commit()
        
        return {
            'profesor': profesor,
            'estudiante': estudiante,
            'total_sesiones': len(sesiones_data)
        }


# ==================== TESTS DE CONTRATO API ====================

class TestAnalyticsEstudianteContract:
    """
    Tests para get_analytics_estudiante()
    Valida que el refactoring no rompa el contrato de la API
    """
    
    def test_estructura_response_basica(self, analytics_service, setup_test_data):
        """Verifica que la respuesta tenga todas las claves esperadas"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        # Claves obligatorias en la respuesta
        assert 'success' in resultado
        assert 'total_sesiones' in resultado
        assert 'estadisticas' in resultado
        assert 'por_maqueta' in resultado
        assert 'progreso_temporal' in resultado
        assert 'insights' in resultado
        assert 'sesiones' in resultado
        
        # success debe ser True cuando hay sesiones
        assert resultado['success'] is True
    
    def test_estadisticas_calculadas_correctamente(self, analytics_service, setup_test_data):
        """Valida que las estadísticas básicas se calculen correctamente"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        estadisticas = resultado['estadisticas']
        
        # Estructura de estadísticas
        assert 'puntaje_promedio' in estadisticas
        assert 'puntaje_maximo' in estadisticas
        assert 'puntaje_minimo' in estadisticas
        assert 'tiempo_promedio_minutos' in estadisticas
        
        # Validar rangos lógicos
        assert 0 <= estadisticas['puntaje_promedio'] <= 5
        assert 0 <= estadisticas['puntaje_maximo'] <= 5
        assert 0 <= estadisticas['puntaje_minimo'] <= 5
        assert estadisticas['puntaje_maximo'] >= estadisticas['puntaje_minimo']
        
        # Puntaje promedio esperado: (4.5 + 3.8 + 4.2 + 3.5 + 4.0) / 5 = 4.0
        assert 3.9 <= estadisticas['puntaje_promedio'] <= 4.1
    
    def test_agrupacion_por_maqueta(self, analytics_service, setup_test_data):
        """Verifica que las sesiones se agrupen correctamente por maqueta"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        por_maqueta = resultado['por_maqueta']
        
        # Debe haber 2 maquetas en los datos de prueba
        assert len(por_maqueta) == 2
        
        # Cada maqueta debe tener estructura correcta
        for maqueta_data in por_maqueta:
            assert 'maqueta' in maqueta_data
            assert 'sesiones' in maqueta_data
            assert 'puntaje_promedio' in maqueta_data
            assert 'mejor' in maqueta_data
            
            assert maqueta_data['sesiones'] > 0
            assert 0 <= maqueta_data['puntaje_promedio'] <= 5
    
    def test_progreso_temporal_estructura(self, analytics_service, setup_test_data):
        """Valida que el progreso temporal tenga la estructura correcta"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        progreso = resultado['progreso_temporal']
        
        # Debe ser un diccionario con maquetas como claves
        assert isinstance(progreso, dict)
        assert len(progreso) > 0
        
        # Cada maqueta debe tener una lista de puntos de progreso
        for maqueta, datos in progreso.items():
            assert isinstance(datos, list)
            
            for punto in datos:
                assert 'puntaje' in punto
                assert 'fecha' in punto
                assert 'fecha_completa' in punto
    
    def test_insights_generados(self, analytics_service, setup_test_data):
        """Verifica que se generen insights para el estudiante"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        insights = resultado['insights']
        
        # Debe haber al menos un insight
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert all(isinstance(insight, str) for insight in insights)
    
    def test_sesiones_serializadas(self, analytics_service, setup_test_data):
        """Valida que las sesiones se serialicen correctamente"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        sesiones = resultado['sesiones']
        
        # Debe haber 5 sesiones
        assert len(sesiones) == 5
        
        # Cada sesión debe tener estructura correcta
        for sesion in sesiones:
            assert 'id' in sesion
            assert 'maqueta' in sesion
            assert 'puntaje' in sesion
            assert 'tiempo_segundos' in sesion
            assert 'interacciones_ia' in sesion
            assert 'fecha' in sesion
            assert 'profesor' in sesion
    
    def test_sin_sesiones_devuelve_estructura_vacia(self, analytics_service, app):
        """Verifica el comportamiento cuando no hay sesiones"""
        with app.app_context():
            # Crear estudiante sin sesiones
            estudiante = Estudiante(
                nombre="Sin Sesiones",
                codigo="NOSESS",
                email="sin@sesiones.com"
            )
            estudiante.set_password("test123")
            db.session.add(estudiante)
            db.session.commit()
            
            resultado = analytics_service.get_analytics_estudiante(estudiante.id)
            
            # Debe devolver success=True pero con datos vacíos
            assert resultado['success'] is True
            assert resultado['total_sesiones'] == 0
            assert resultado['estadisticas']['puntaje_promedio'] == 0


class TestAnalyticsEstudiantePorProfesorContract:
    """
    Tests para get_analytics_estudiante_por_profesor()
    Debe tener el MISMO contrato que get_analytics_estudiante() + datos del profesor
    """
    
    def test_estructura_response_con_profesor(self, analytics_service, setup_test_data):
        """Verifica que incluya datos del profesor además de las estadísticas"""
        estudiante_id = setup_test_data['estudiante'].id
        profesor_id = setup_test_data['profesor'].id
        
        resultado = analytics_service.get_analytics_estudiante_por_profesor(
            estudiante_id, profesor_id
        )
        
        # Mismo contrato que get_analytics_estudiante
        assert 'success' in resultado
        assert 'total_sesiones' in resultado
        assert 'estadisticas' in resultado
        assert 'por_maqueta' in resultado
        assert 'progreso_temporal' in resultado
        assert 'insights' in resultado
        assert 'sesiones' in resultado
        
        # PLUS: Información del profesor
        assert 'profesor' in resultado
        assert resultado['profesor']['id'] == profesor_id
        assert 'nombre' in resultado['profesor']
        assert 'institucion' in resultado['profesor']
    
    def test_filtra_solo_sesiones_del_profesor(self, analytics_service, setup_test_data, app):
        """Verifica que solo cuente sesiones del profesor especificado"""
        with app.app_context():
            estudiante_id = setup_test_data['estudiante'].id
            profesor_id = setup_test_data['profesor'].id
            
            # Crear otro profesor y una sesión con él
            otro_profesor = Profesor(
                nombre="Otro Profesor",
                email="otro@test.com",
                institucion="Otra U"
            )
            otro_profesor.set_password("test123")
            db.session.add(otro_profesor)
            db.session.commit()
            
            # Agregar sesión con el otro profesor
            sesion_extra = Sesion(
                estudiante_id=estudiante_id,
                profesor_id=otro_profesor.id,
                maqueta="Cardiaca",
                puntaje=3.0,
                tiempo_segundos=1800,
                interacciones_ia=10,
                fecha=datetime.now()
            )
            db.session.add(sesion_extra)
            db.session.commit()
            
            # Obtener analytics del primer profesor
            resultado = analytics_service.get_analytics_estudiante_por_profesor(
                estudiante_id, profesor_id
            )
            
            # Debe tener solo las 5 sesiones originales, NO la 6ta
            assert resultado['total_sesiones'] == 5
            
            # Todas las sesiones deben ser del profesor correcto
            for sesion in resultado['sesiones']:
                assert sesion['profesor']['id'] == profesor_id
    
    def test_estadisticas_identicas_a_get_analytics_estudiante(self, analytics_service, setup_test_data):
        """
        CRÍTICO: Cuando el estudiante solo tiene sesiones con 1 profesor,
        ambos métodos deben devolver las MISMAS estadísticas
        """
        estudiante_id = setup_test_data['estudiante'].id
        profesor_id = setup_test_data['profesor'].id
        
        # Llamar a ambos métodos
        resultado_general = analytics_service.get_analytics_estudiante(estudiante_id)
        resultado_filtrado = analytics_service.get_analytics_estudiante_por_profesor(
            estudiante_id, profesor_id
        )
        
        # Estadísticas deben ser IDÉNTICAS
        assert resultado_general['total_sesiones'] == resultado_filtrado['total_sesiones']
        assert resultado_general['estadisticas'] == resultado_filtrado['estadisticas']
        assert len(resultado_general['por_maqueta']) == len(resultado_filtrado['por_maqueta'])
    
    def test_profesor_inexistente(self, analytics_service, setup_test_data):
        """Verifica el manejo de profesor que no existe"""
        estudiante_id = setup_test_data['estudiante'].id
        profesor_falso_id = 99999
        
        resultado = analytics_service.get_analytics_estudiante_por_profesor(
            estudiante_id, profesor_falso_id
        )
        
        # Debe devolver error
        assert resultado['success'] is False
        assert 'message' in resultado


# ==================== TESTS DE REFACTORING ====================

class TestRefactoringIntegrity:
    """
    Tests específicos para validar que el refactoring no introduce bugs
    """
    
    def test_calculo_tiempo_promedio_consistente(self, analytics_service, setup_test_data):
        """Valida que el tiempo promedio se calcule igual antes y después"""
        estudiante_id = setup_test_data['estudiante'].id
        profesor_id = setup_test_data['profesor'].id
        
        resultado_general = analytics_service.get_analytics_estudiante(estudiante_id)
        resultado_filtrado = analytics_service.get_analytics_estudiante_por_profesor(
            estudiante_id, profesor_id
        )
        
        # Tiempo promedio: (1800 + 2100 + 1950 + 2400 + 2200) / 5 / 60 = ~34.17 minutos
        tiempo_esperado = 34.0  # Aproximado
        
        assert abs(resultado_general['estadisticas']['tiempo_promedio_minutos'] - tiempo_esperado) < 1
        assert abs(resultado_filtrado['estadisticas']['tiempo_promedio_minutos'] - tiempo_esperado) < 1
    
    def test_ordenamiento_progreso_temporal(self, analytics_service, setup_test_data):
        """Verifica que el progreso temporal esté ordenado cronológicamente"""
        estudiante_id = setup_test_data['estudiante'].id
        resultado = analytics_service.get_analytics_estudiante(estudiante_id)
        
        progreso = resultado['progreso_temporal']
        
        for maqueta, datos in progreso.items():
            if len(datos) > 1:
                # Verificar que las fechas estén en orden ascendente
                fechas = [datetime.strptime(p['fecha_completa'], '%Y-%m-%d') for p in datos]
                assert fechas == sorted(fechas), f"Progreso temporal de {maqueta} no está ordenado"
    
    def test_performance_no_degradada(self, analytics_service, setup_test_data):
        """Verifica que el refactoring no degrade el rendimiento"""
        import time
        
        estudiante_id = setup_test_data['estudiante'].id
        
        # Medir tiempo de ejecución
        start = time.time()
        analytics_service.get_analytics_estudiante(estudiante_id)
        duracion = time.time() - start
        
        # Debe ejecutarse en menos de 1 segundo (generoso para CI)
        assert duracion < 1.0, f"Performance degradada: {duracion:.3f}s"
