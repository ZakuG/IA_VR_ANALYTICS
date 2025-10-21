# Tests - VR Analytics

Este directorio contiene todos los tests unitarios e integración del proyecto.

## Estructura

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── test_app.py              # Tests de rutas Flask
├── test_services/
│   ├── test_analytics_service.py
│   ├── test_auth_service.py
│   └── test_session_service.py
├── test_repositories/
│   ├── test_session_repository.py
│   ├── test_profesor_repository.py
│   └── test_estudiante_repository.py
└── test_utils/
    ├── test_validators.py
    └── test_decorators.py
```

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov=services --cov=repositories --cov=utils --cov-report=html

# Tests específicos
pytest tests/test_services/

# Ver cobertura en navegador
start htmlcov/index.html
```

## Convenciones

- Usar `pytest` como framework
- Fixtures en `conftest.py`
- Nombres de test: `test_descripcion_del_caso()`
- Usar mocks para dependencias externas
