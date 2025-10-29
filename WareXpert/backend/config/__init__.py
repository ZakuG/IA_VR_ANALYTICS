"""
WareXpert Configuration Package
Provides configuration classes for different environments
"""

from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env='default'):
    """
    Get configuration object based on environment
    
    Args:
        env (str): Environment name (development, production, testing)
        
    Returns:
        Config: Configuration class for the specified environment
    """
    return config_by_name.get(env, config_by_name['default'])
