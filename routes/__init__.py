"""
📁 Routes Package - Blueprints de Flask
========================================

Este paquete organiza las rutas de la aplicación en blueprints
separados según su funcionalidad, siguiendo el principio de
Single Responsibility (SOLID).

Blueprints disponibles:
- auth_bp: Autenticación (login, register, logout, password recovery)
- dashboard_bp: Dashboards (profesor y estudiante)
- api_bp: API REST endpoints para analytics
- estudiante_bp: Rutas específicas de estudiantes
- unity_bp: Endpoints para integración con Unity VR

Uso:
    from routes import register_blueprints
    register_blueprints(app)
"""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    """
    Registra todos los blueprints de la aplicación.
    
    Args:
        app: Instancia de Flask
    
    Returns:
        None
    
    Example:
        >>> from flask import Flask
        >>> app = Flask(__name__)
        >>> register_blueprints(app)
    """
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.api_routes import api_bp
    from routes.estudiante_routes import estudiante_bp
    from routes.unity_routes import unity_bp
    
    # Registrar blueprints con sus prefijos
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(estudiante_bp, url_prefix='/api/estudiante')
    app.register_blueprint(unity_bp, url_prefix='/api/unity')
    
    # Log de blueprints registrados
    app.logger.info("✅ Blueprints registrados exitosamente")
    app.logger.debug(f"Total blueprints: 5 (auth, dashboard, api, estudiante, unity)")


__all__ = ['register_blueprints']
