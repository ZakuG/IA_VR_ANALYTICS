# 📋 Plan de Sprint de Mantenimiento - VR Analytics
## Actividad: Primer Sprint de Mantenimiento

**Fecha:** Octubre 2025  
**Proyecto:** Sistema VR Analytics (Flask + ML)  
**Equipo:** Taller de Ingeniería de Software

---

## 1️⃣ Auditoría Rápida - Matriz de Issues

### Tabla de Clasificación de Issues

| Issue | Tipo | Severidad | Impacto | Evidencia | Estado |
|-------|------|-----------|---------|-----------|--------|
| #1: Statements print() en producción | **Correctivo** | S1 (Crítica) | Alto | 20+ prints en app.py, logs visibles en consola producción | 🔴 Abierto |
| #2: Dependencias desactualizadas | **Adaptativo** | S2 (Alta) | Alto | Flask 3.0.0 → 3.1.0, scikit-learn 1.3.2 → 1.5.2 disponible | 🔴 Abierto |
| #3: Código duplicado en analytics | **Perfectivo** | S3 (Media) | Medio | Lógica repetida en `get_analytics_estudiante()` y `get_analytics_estudiante_por_profesor()` | 🔴 Abierto |
| #4: Sin configuración de linter | **Preventivo** | S4 (Baja) | Medio | No hay .flake8, black.toml, ni pre-commit hooks | 🔴 Abierto |

---

## 2️⃣ Issues Seleccionados para el Sprint

### 🔴 Issue #1 - Correctivo: Eliminar prints de debug en producción
**Descripción:**  
El código contiene más de 20 statements `print()` de debug en `app.py`, `services/analytics_service.py`, y otros módulos. Esto expone información sensible en logs de producción y degrada el rendimiento.

**Criterios de Aceptación:**
- ✅ Todos los `print()` de debug reemplazados por `logging`
- ✅ Configuración de logging profesional con niveles (DEBUG, INFO, WARNING, ERROR)
- ✅ Test que verifica que no hay prints en producción
- ✅ CI pasa sin warnings

**Archivos afectados:**
- `app.py` (líneas 63, 137, 272, 282, 286, 296, 383, 492-499, 553-555)
- `services/analytics_service.py`
- `data_analytics.py`

**Prioridad:** 🔴 Alta (S1 - Crítica)

---

### 🟡 Issue #2 - Adaptativo: Actualizar dependencias críticas
**Descripción:**  
Varias dependencias tienen versiones más recientes con mejoras de seguridad y rendimiento:
- Flask 3.0.0 → 3.1.0 (nuevas features y fixes)
- scikit-learn 1.3.2 → 1.5.2 (mejoras ML)
- pandas 2.1.3 → 2.2.3 (performance)

**Criterios de Aceptación:**
- ✅ `requirements.txt` actualizado con versiones compatibles
- ✅ Tests existentes pasan con nuevas versiones
- ✅ Verificación de breaking changes documentada
- ✅ CI pasa en verde

**Archivos afectados:**
- `requirements.txt`
- Posibles ajustes en código si hay breaking changes

**Prioridad:** 🟡 Alta (S2)

---

### 🟠 Issue #3 - Perfectivo: Refactorizar métodos duplicados en AnalyticsService
**Descripción:**  
Los métodos `get_analytics_estudiante()` y `get_analytics_estudiante_por_profesor()` tienen lógica casi idéntica (80% duplicación). Esto viola DRY y dificulta mantenimiento.

**Criterios de Aceptación:**
- ✅ Extraer lógica común a método privado `_calcular_estadisticas_base()`
- ✅ Sin cambios en contrato público (API responses iguales)
- ✅ Reducción de líneas de código >40%
- ✅ Tests de integración pasan

**Archivos afectados:**
- `services/analytics_service.py` (líneas 90-200 aprox)

**Prioridad:** 🟠 Media (S3)

---

### 🟢 Issue #4 - Preventivo: Configurar linter y herramientas de calidad
**Descripción:**  
El proyecto no tiene configuración de herramientas de calidad de código (linter, formatter, pre-commit hooks). Esto permite que código inconsistente llegue al repositorio.

**Criterios de Aceptación:**
- ✅ Configuración de `flake8` con reglas personalizadas
- ✅ Configuración de `black` para formato automático
- ✅ Pre-commit hooks instalados
- ✅ CI ejecuta linter y falla si hay errores
- ✅ Código existente pasa linter sin errores

**Archivos afectados:**
- `.flake8` (nuevo)
- `pyproject.toml` (nuevo)
- `.pre-commit-config.yaml` (nuevo)
- `.github/workflows/ci.yml` (nuevo)

**Prioridad:** 🟢 Baja (S4)

---

## 3️⃣ Línea Base (ANTES del Sprint)

### Métricas Iniciales

```bash
# Ejecutar para medir estado actual
pytest --cov=services --cov=repositories --cov-report=term-missing
pytest --cov=data_analytics --cov-report=term-missing
```

**Resultados esperados:**

| Métrica | Valor Inicial | Objetivo | Método de Medición |
|---------|--------------|----------|-------------------|
| Cobertura `services/` | ? % | ≥60% | `pytest --cov=services` |
| Cobertura `data_analytics.py` | ? % | +15 pp | `pytest --cov=data_analytics` |
| Errores de linter | N/A | 0 | `flake8 .` (después de config) |
| Prints en código | ~25 | 0 | `grep -r "print(" --include="*.py"` |
| Dependencias desactualizadas | 3 | 0 | `pip list --outdated` |
| Tiempo de build CI | N/A | <2 min | GitHub Actions |

---

## 4️⃣ Cronograma de Implementación

### Día 1 - Planificación y Diagnóstico ✅
- [x] Auditoría de código y creación de matriz de issues
- [x] Selección de 4 issues (uno de cada tipo)
- [x] Definición de criterios de aceptación
- [x] Medición de línea base

### Día 2 - Implementación (Issues Críticos)
- [ ] **PR #1** - Issue Correctivo: Reemplazar prints por logging
- [ ] **PR #2** - Issue Adaptativo: Actualizar dependencias

### Día 3 - Implementación (Issues de Mejora)
- [ ] **PR #3** - Issue Perfectivo: Refactorizar analytics duplicado
- [ ] **PR #4** - Issue Preventivo: Configurar linter y CI

### Día 4 - Medición y Reporte
- [ ] Medir métricas finales (cobertura, linter, CI)
- [ ] Crear reporte de resultados
- [ ] Documentar lecciones aprendidas

---

## 5️⃣ Plantilla de Pull Request

**Ubicación:** `.github/pull_request_template.md`

```markdown
[TIPO] Título corto (Issue #___)

## Contexto
Qué problema había / qué motivó el cambio.

## Solución
Qué se cambió y por qué.

## Pruebas
- Nuevos tests: [lista]
- Resultados locales: OK

## Checklist
- [ ] Linter OK
- [ ] CI OK
- [ ] Cambios atómicos (sin mezclar temas)
- [ ] Documentación actualizada
- [ ] Tests pasan localmente
```

---

## 6️⃣ Comandos Útiles

### Para tests y cobertura
```bash
# Instalar dependencias de testing
pip install pytest pytest-cov

# Ejecutar tests con cobertura
pytest --cov=services --cov=repositories --cov=data_analytics --cov-report=html

# Ver reporte en navegador
start htmlcov/index.html  # Windows
```

### Para linter (después de Issue #4)
```bash
# Instalar herramientas
pip install flake8 black isort pre-commit

# Ejecutar linter
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Auto-format código
black .
isort .

# Instalar pre-commit hooks
pre-commit install
```

### Para dependencias
```bash
# Ver dependencias desactualizadas
pip list --outdated

# Actualizar requirements.txt
pip freeze > requirements.txt
```

---

## 7️⃣ Roles del Equipo

| Rol | Responsable | Responsabilidades |
|-----|-------------|-------------------|
| **Maintainer** | [Nombre] | Coordina sprint, revisa PRs, aprueba merges |
| **Tester** | [Nombre] | Escribe tests, mide cobertura, valida CI |
| **Dev** | [Nombre] | Implementa cambios atómicos por issue |
| **Scribe** | [Nombre] | Documenta métricas, crea reporte final |

---

## 8️⃣ Definición de "Hecho" (DoD)

Un issue se considera completado cuando:

1. ✅ Código implementado cumple criterios de aceptación
2. ✅ Tests escritos y pasando (cobertura ≥60% del módulo)
3. ✅ PR revisado y aprobado por Maintainer
4. ✅ CI en verde (tests + linter)
5. ✅ Documentación actualizada si aplica
6. ✅ Merge a `main` completado

---

## 9️⃣ Métricas de Éxito

Al final del sprint:

- **Correctivo:** 0 prints de debug en código producción ✅
- **Adaptativo:** 0 dependencias críticas desactualizadas ✅
- **Perfectivo:** Reducción >40% líneas duplicadas ✅
- **Preventivo:** CI configurado y pasando + linter activo ✅
- **Cobertura:** `services/` y `data_analytics` ≥60% ✅

---

## 📚 Referencias

- [Guía de Mantenimiento de Software - IEEE](https://ieeexplore.ieee.org/)
- [Python Testing Best Practices](https://docs.pytest.org/)
- [Flask Testing Guide](https://flask.palletsprojects.com/en/latest/testing/)
- [PEP 8 - Style Guide for Python](https://peps.python.org/pep-0008/)

---

**Última actualización:** Octubre 2025  
**Versión:** 1.0
