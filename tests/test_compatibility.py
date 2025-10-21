"""
Tests de compatibilidad de dependencias actualizadas
Issue #2 - Adaptativo
"""
import pytest
import sys


def test_flask_version():
    """Verifica que Flask esté en versión 3.1.x"""
    import flask
    version = flask.__version__
    major, minor, _ = version.split('.')
    assert major == '3', f"Flask major version should be 3, got {major}"
    assert int(minor) >= 1, f"Flask minor version should be ≥1, got {minor}"


def test_pandas_version():
    """Verifica que pandas esté en versión 2.2.x+"""
    import pandas as pd
    version = pd.__version__
    major, minor, *_ = version.split('.')
    assert major == '2', f"Pandas major version should be 2, got {major}"
    assert int(minor) >= 2, f"Pandas minor version should be ≥2, got {minor}"


def test_numpy_version():
    """Verifica que numpy esté en versión 1.26.x (no 2.x por ahora)"""
    import numpy as np
    version = np.__version__
    major, minor, *_ = version.split('.')
    assert major == '1', f"Numpy major version should be 1, got {major}"
    assert int(minor) >= 26, f"Numpy minor version should be ≥26, got {minor}"


def test_sklearn_version():
    """Verifica que scikit-learn esté en versión 1.5.x+"""
    import sklearn
    version = sklearn.__version__
    major, minor, *_ = version.split('.')
    assert major == '1', f"Scikit-learn major version should be 1, got {major}"
    assert int(minor) >= 5, f"Scikit-learn minor version should be ≥5, got {minor}"


def test_scipy_version():
    """Verifica que scipy esté en versión 1.14.x+"""
    import scipy
    version = scipy.__version__
    major, minor, *_ = version.split('.')
    assert major == '1', f"Scipy major version should be 1, got {major}"
    assert int(minor) >= 14, f"Scipy minor version should be ≥14, got {minor}"


def test_werkzeug_version():
    """Verifica que Werkzeug esté en versión 3.1.x+"""
    from importlib.metadata import version
    werkzeug_version = version('werkzeug')
    major, minor, *_ = werkzeug_version.split('.')
    assert major == '3', f"Werkzeug major version should be 3, got {major}"
    assert int(minor) >= 1, f"Werkzeug minor version should be ≥1, got {minor}"


def test_import_data_analytics():
    """Verifica que data_analytics se puede importar sin errores"""
    try:
        import sys
        import os
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from data_analytics import AnalizadorAvanzado
        assert AnalizadorAvanzado is not None
    except ImportError as e:
        pytest.fail(f"Failed to import data_analytics: {e}")


def test_pandas_operations():
    """Verifica operaciones básicas de pandas funcionan"""
    import pandas as pd
    import numpy as np
    
    # Crear DataFrame de prueba
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50],
        'C': ['a', 'b', 'c', 'd', 'e']
    })
    
    # Operaciones comunes
    assert len(df) == 5
    assert df['A'].mean() == 3.0
    assert df['B'].sum() == 150
    assert df.groupby('C')['A'].sum()['a'] == 1


def test_numpy_operations():
    """Verifica operaciones básicas de numpy funcionan"""
    import numpy as np
    
    # Operaciones comunes
    arr = np.array([1, 2, 3, 4, 5])
    assert arr.mean() == 3.0
    assert arr.std() > 0
    assert np.max(arr) == 5


def test_sklearn_operations():
    """Verifica que scikit-learn funciona correctamente"""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import numpy as np
    
    # Datos de prueba
    X = np.array([[1, 2], [1, 4], [1, 0], [10, 2], [10, 4], [10, 0]])
    
    # KMeans (usado en data_analytics.py)
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    kmeans.fit(X)
    assert len(kmeans.labels_) == 6
    assert len(set(kmeans.labels_)) == 2
    
    # StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    assert X_scaled.shape == X.shape


def test_no_deprecation_warnings_on_import():
    """Verifica que no hay warnings al importar módulos principales"""
    import warnings
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Importar módulos principales
        import flask
        import pandas as pd
        import numpy as np
        import sklearn
        import scipy
        
        # Filtrar solo DeprecationWarning y FutureWarning
        dep_warnings = [warning for warning in w 
                       if issubclass(warning.category, (DeprecationWarning, FutureWarning))]
        
        if dep_warnings:
            warnings_str = "\n".join(str(w.message) for w in dep_warnings)
            pytest.fail(f"Found deprecation warnings:\n{warnings_str}")


def test_flask_app_can_start():
    """Verifica que la app Flask puede inicializarse con nuevas versiones"""
    try:
        import sys
        import os
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import app
        assert app is not None
        assert app.name == 'app'
    except Exception as e:
        pytest.fail(f"Failed to import Flask app: {e}")
