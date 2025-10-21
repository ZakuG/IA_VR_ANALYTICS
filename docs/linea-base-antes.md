# 📊 Línea Base - Sprint de Mantenimiento
## Métricas ANTES del Sprint

**Fecha de medición:** 20 de Octubre 2025  
**Branch:** main

---

## 1️⃣ Análisis de Código

### Prints de Debug en Producción
```bash
Comando: grep -r "print(" --include="*.py" | wc -l
```

**Archivos con prints:**
- `app.py`: 20+ prints de debug
- `migrate_db.py`: 15+ prints
- `services/analytics_service.py`: Posibles prints
- `data_analytics.py`: Posibles prints

**Total estimado:** ~40-50 statements print()

---

## 2️⃣ Dependencias Desactualizadas

### Dependencias Críticas
| Paquete | Versión Actual | Versión Latest | Tipo de Actualización |
|---------|----------------|----------------|----------------------|
| **Flask** | 3.0.0 | 3.1.2 | Minor (features + fixes) |
| **numpy** | 1.26.2 | 2.3.4 | **Major** (breaking changes) |
| **pandas** | 2.1.3 | 2.3.3 | Minor (performance) |
| **scikit-learn** | 1.3.2 | 1.7.2 | Minor (ML improvements) |
| **scipy** | 1.11.4 | 1.16.2 | Minor |
| **Werkzeug** | 3.0.1 | 3.1.3 | Minor (seguridad) |
| **MarkupSafe** | 2.1.2 | 3.0.3 | **Major** |

### Análisis de Riesgo
- 🔴 **Alto:** numpy 1.x → 2.x (breaking changes en API)
- 🟡 **Medio:** MarkupSafe 2.x → 3.x
- 🟢 **Bajo:** Flask, pandas, scikit-learn (minor updates)

**Total paquetes desactualizados:** 80+ (según pip list --outdated)

---

## 3️⃣ Calidad de Código

### Linter/Formatter
- ❌ **No configurado:** flake8
- ❌ **No configurado:** black
- ❌ **No configurado:** isort
- ❌ **No configurado:** pre-commit hooks

### Archivos de configuración faltantes
- `.flake8` - No existe
- `pyproject.toml` - No existe
- `.pre-commit-config.yaml` - No existe

---

## 4️⃣ Testing y Cobertura

### Estado de Tests
```bash
# No hay carpeta tests/ en el proyecto
# No hay archivos test_*.py
```

**Resultado:** ❌ **0% de cobertura** (no hay tests implementados)

### Módulos sin tests
- ✅ `app.py` (696 líneas) - 0% cobertura
- ✅ `services/analytics_service.py` (373 líneas) - 0% cobertura
- ✅ `services/auth_service.py` - 0% cobertura
- ✅ `services/session_service.py` - 0% cobertura
- ✅ `repositories/*.py` - 0% cobertura
- ✅ `data_analytics.py` (816 líneas) - 0% cobertura
- ✅ `utils/*.py` - 0% cobertura

---

## 5️⃣ CI/CD

### GitHub Actions
- ❌ **No configurado:** `.github/workflows/` vacío o no existe
- ❌ **No hay CI:** tests no se ejecutan automáticamente
- ❌ **No hay linter:** en CI

### Estado del repositorio
- ✅ Git configurado
- ✅ `.gitignore` presente
- ❌ CI/CD pipeline ausente

---

## 6️⃣ Documentación

### Documentación existente
- ✅ `README.md` - Presente
- ✅ `ARQUITECTURA_SOFTWARE.md` - Excelente (400 líneas)
- ✅ `PATRONES_DISEÑO_EJEMPLOS.md` - Excelente (600 líneas)
- ✅ `PRESENTACION_EJECUTIVA.md` - Completo
- ✅ `DIAGRAMAS_VISUALES.md` - Visual aids
- ✅ `GUIA_RAPIDA_PRESENTACION.md` - Quick reference
- ❌ Documentación de tests - No existe

---

## 7️⃣ Código Duplicado

### Analytics Service
**Métodos con duplicación detectada:**
```python
# services/analytics_service.py
- get_analytics_estudiante() (líneas ~90-150)
- get_analytics_estudiante_por_profesor() (líneas ~150-210)
```

**Estimación de duplicación:** ~80% de código similar

**Líneas duplicadas:** ~50-60 líneas

---

## 8️⃣ Resumen de Métricas Iniciales

| Métrica | Valor ANTES | Objetivo | Estado |
|---------|-------------|----------|--------|
| **Prints en código** | ~40-50 | 0 | 🔴 Crítico |
| **Cobertura total** | 0% | ≥60% módulo crítico | 🔴 Crítico |
| **Dependencias desactualizadas** | 80+ (3 críticas) | 0 críticas | 🟡 Alto |
| **Errores de linter** | N/A (no config) | 0 | 🟡 Medio |
| **Código duplicado** | ~60 líneas | <20 líneas | 🟢 Bajo |
| **CI/CD** | No existe | Pipeline funcional | 🔴 Crítico |
| **Pre-commit hooks** | No existe | Configurado | 🟢 Bajo |

---

## 9️⃣ Issues Priorizados

Basado en el análisis:

1. **🔴 CRÍTICO - Issue #1:** Reemplazar prints por logging
2. **🟡 ALTO - Issue #2:** Actualizar dependencias (Flask, scikit-learn, pandas)
3. **🟠 MEDIO - Issue #3:** Refactorizar código duplicado en analytics
4. **🟢 BAJO - Issue #4:** Configurar linter y pre-commit hooks

---

## 📝 Notas

### Hallazgos adicionales
1. **Positivo:** Arquitectura bien documentada (6 documentos MD)
2. **Positivo:** Patrón Repository y Service Layer bien implementados
3. **Negativo:** Ausencia total de tests unitarios
4. **Negativo:** numpy 1.x → 2.x requiere atención (breaking changes)
5. **Recomendación:** Considerar pytest + pytest-cov para testing

### Prioridades del Sprint
- **Día 1:** Issue #1 (prints) + crear estructura de tests ✅
- **Día 2:** Issue #2 (dependencias) con cuidado en numpy
- **Día 3:** Issue #3 (refactor) + Issue #4 (linter)

---

**Medición realizada por:** Equipo Taller de Software  
**Próxima medición:** Fin del Sprint (Día 4)
