"""API Routes Package - Registers all API endpoints and blueprints"""
from flask import Blueprint, jsonify

# Health check blueprint (no authentication required)
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - Returns API status and version"""
    return jsonify({
        'status': 'healthy',
        'service': 'WareXpert API',
        'version': '1.0.0',
        'environment': 'development'
    }), 200

@health_bp.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint - Tests database and Redis connectivity"""
    from app import db
    
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # TODO: Test Redis connection
    redis_status = 'not_configured'
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'service': 'WareXpert API',
        'version': '1.0.0',
        'checks': {
            'database': db_status,
            'redis': redis_status
        }
    }), 200 if db_status == 'connected' else 503


# Import route blueprints
from app.routes.auth import auth_bp
from app.routes.warehouses import warehouses_bp
from app.routes.products import products_bp

__all__ = ['health_bp', 'auth_bp', 'warehouses_bp', 'products_bp']

