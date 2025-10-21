# Actualización de Dependencias - Análisis y Estrategia

## Dependencias Críticas Identificadas

### 🔴 Actualización con Precaución (Breaking Changes)

#### 1. numpy: 1.26.2 → 2.3.4 ⚠️ MAJOR VERSION
**Breaking Changes Conocidos:**
- Cambios en API de arrays
- Deprecación de funciones antiguas
- Cambios en comportamiento de operaciones
- Impacto potencial alto en pandas y scikit-learn

**Estrategia:** 🛑 **NO actualizar en este sprint**
- Requiere testing extensivo
- Posible incompatibilidad con pandas 2.1.3
- Mejor esperar a pandas 2.3.x que soporta numpy 2.x oficialmente

---

### 🟡 Actualizaciones Seguras (Minor/Patch)

#### 2. Flask: 3.0.0 → 3.1.2 ✅ SAFE
**Cambios:**
- Mejoras de seguridad
- Nuevas features opcionales
- Bug fixes

**Acción:** ✅ Actualizar

#### 3. pandas: 2.1.3 → 2.2.3 ✅ SAFE (pero con numpy 1.x)
**Cambios:**
- Mejoras de performance
- Bug fixes
- Compatible con numpy 1.26.x

**Acción:** ✅ Actualizar (mantener numpy 1.x)

#### 4. scikit-learn: 1.3.2 → 1.5.2 ✅ SAFE
**Cambios:**
- Mejoras ML
- Nuevos algoritmos
- Bug fixes

**Acción:** ✅ Actualizar

#### 5. scipy: 1.11.4 → 1.14.1 ✅ SAFE
**Cambios:**
- Mejoras de performance
- Bug fixes

**Acción:** ✅ Actualizar

#### 6. Werkzeug: 3.0.1 → 3.1.3 ✅ SAFE
**Cambios:**
- Parches de seguridad
- Bug fixes

**Acción:** ✅ Actualizar

#### 7. Flask-Bcrypt: 1.0.1 → 1.0.1 (OK)
**Estado:** Ya está actualizado

#### 8. Flask-Login: 0.6.3 → 0.6.3 (OK)
**Estado:** Ya está actualizado

---

## Plan de Actualización Fase 1 (Sprint Actual)

### requirements.txt objetivo:
```
# Core Framework
Flask==3.1.2              # 3.0.0 → 3.1.2 ✅
Flask-SQLAlchemy==3.1.1   # OK
Flask-Bcrypt==1.0.1       # OK
Flask-Login==0.6.3        # OK
Werkzeug==3.1.3           # 3.0.1 → 3.1.3 ✅

# Data Science (mantener numpy 1.x)
pandas==2.2.3             # 2.1.3 → 2.2.3 ✅
numpy==1.26.4             # 1.26.2 → 1.26.4 (última de 1.x) ✅
scipy==1.14.1             # 1.11.4 → 1.14.1 ✅
scikit-learn==1.5.2       # 1.3.2 → 1.5.2 ✅

# Utilities
python-dotenv==1.0.1      # 1.0.0 → 1.0.1 ✅

# Testing
pytest==8.4.2             # 8.4.1 → 8.4.2 ✅
pytest-cov==7.0.0         # OK
coverage==7.11.0          # OK
```

---

## Tests de Compatibilidad

### Test 1: Importación de módulos
```python
import flask
import pandas as pd
import numpy as np
import sklearn
import scipy

assert flask.__version__ == '3.1.2'
assert pd.__version__ == '2.2.3'
assert np.__version__.startswith('1.26')
```

### Test 2: Funcionalidad data_analytics
```python
from data_analytics import AnalizadorAvanzado

# Verificar que clustering funciona
# Verificar que predicciones funcionan
```

### Test 3: Endpoints Flask
```bash
pytest tests/  # Todos los tests deben pasar
```

---

## Riesgos y Mitigación

### Riesgo 1: scikit-learn 1.5.x cambios en API
**Mitigación:**
- Ejecutar tests de ML
- Verificar warnings de deprecación
- Revisar changelog: https://scikit-learn.org/stable/whats_new/v1.5.html

### Riesgo 2: pandas 2.2.x cambios de comportamiento
**Mitigación:**
- Tests de análisis de datos
- Verificar operaciones groupby, merge, etc.
- Revisar changelog: https://pandas.pydata.org/docs/whatsnew/v2.2.0.html

### Riesgo 3: Flask 3.1.x cambios en routing
**Mitigación:**
- Tests de integración de rutas
- Verificar decoradores personalizados
- Changelog: https://flask.palletsprojects.com/en/3.1.x/changes/

---

## Criterios de Aceptación

- ✅ `pip install -r requirements.txt` funciona sin errores
- ✅ `python app.py` inicia sin warnings de deprecación
- ✅ Todos los tests pasan: `pytest tests/ -v`
- ✅ Endpoints clave responden correctamente:
  - `/api/analytics`
  - `/api/estudiante/analytics`
  - `/api/session/manual`
- ✅ Funciones ML funcionan (clustering, predicción, correlaciones)
- ✅ No hay warnings de FutureWarning o DeprecationWarning

---

## Fase 2 (Sprint Futuro)

**numpy 2.x Migration:**
1. Actualizar pandas a 2.3.x (soporte oficial numpy 2.x)
2. Actualizar scikit-learn a versión compatible
3. Refactorizar código que use APIs deprecadas
4. Testing extensivo
5. Documentar breaking changes

**Estimación:** 1-2 sprints adicionales

---

## Comandos para Actualización

```bash
# 1. Crear requirements-new.txt con versiones actualizadas
# 2. Instalar en ambiente de testing
pip install -r requirements-new.txt

# 3. Ejecutar tests
pytest tests/ -v

# 4. Ejecutar app manualmente
python app.py

# 5. Si todo OK, reemplazar requirements.txt
```

---

**Última revisión:** Octubre 2025  
**Estado:** Listo para implementación
