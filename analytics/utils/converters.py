"""
Módulo de conversión de tipos
Convierte tipos NumPy/Pandas a tipos nativos Python para JSON
"""

import numpy as np
import pandas as pd


def convert_to_native_types(obj):
    """
    Convierte tipos NumPy/Pandas a tipos nativos de Python para JSON
    
    Args:
        obj: Objeto a convertir (puede ser dict, list, numpy, pandas, etc.)
        
    Returns:
        Objeto con tipos nativos de Python
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        # Sanitizar NaN, inf, -inf para JSON
        if np.isnan(obj) or np.isinf(obj):
            return 0
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    return obj
