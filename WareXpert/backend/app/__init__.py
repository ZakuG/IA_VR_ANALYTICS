"""
WareXpert Application Package
Main application factory and initialization
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"]
)

def create_app(config_name='development'):
    """
    Application factory pattern
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from config import get_config
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    
    # Initialize Redis
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup middleware
    setup_middleware(app)
    
    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'app': app}
    
    return app

def register_blueprints(app):
    """Register Flask blueprints (routes)"""
    from app.routes import health_bp, auth_bp, warehouses_bp, products_bp
    
    # Health check endpoint (no authentication required)
    app.register_blueprint(health_bp)
    
    # Authentication routes
    app.register_blueprint(auth_bp)
    
    # Warehouse and location routes
    app.register_blueprint(warehouses_bp)
    
    # Product routes
    app.register_blueprint(products_bp)
    
    app.logger.info('All blueprints registered successfully')

def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'Insufficient permissions'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Too Many Requests', 'message': str(error.description)}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal server error: {error}')
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500

def setup_middleware(app):
    """Setup middleware for request/response processing"""
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        # TODO: Add tenant_id injection middleware in Sprint 1
        pass
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

def setup_logging(app):
    """Configure logging for the application"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Setup file handler with rotation
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/warexpert.log'),
            maxBytes=10240000,  # 10 MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(log_level)
        app.logger.info('WareXpert startup')
