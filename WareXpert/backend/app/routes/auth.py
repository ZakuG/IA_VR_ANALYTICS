"""Authentication routes for login, registration, and token management."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from marshmallow import ValidationError
from datetime import timedelta
from app import db
from app.models.user import User
from app.schemas.auth import (
    LoginSchema,
    TokenSchema,
    RefreshTokenSchema,
    UserSchema,
    ChangePasswordSchema
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Schema instances
login_schema = LoginSchema()
token_schema = TokenSchema()
user_schema = UserSchema()


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint.
    
    Request Body:
        - email: User email
        - password: User password
        - remember_me: Optional, extends token expiry
        
    Returns:
        - access_token: JWT access token
        - refresh_token: JWT refresh token
        - user: User data
    """
    try:
        # Validate request data
        data = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Create tokens
    expires_delta = timedelta(days=7) if data.get('remember_me') else timedelta(hours=1)
    
    additional_claims = {
        'tenant_id': user.tenant_id,
        'role': user.role
    }
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims,
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token = create_refresh_token(
        identity=user.id,
        additional_claims=additional_claims,
        expires_delta=expires_delta
    )
    
    # Update last login
    user.last_login = db.func.now()
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 900,  # 15 minutes in seconds
        'user': user_schema.dump(user)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token.
    
    Returns:
        - access_token: New JWT access token
    """
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    additional_claims = {
        'tenant_id': claims.get('tenant_id'),
        'role': claims.get('role')
    }
    
    access_token = create_access_token(
        identity=current_user_id,
        additional_claims=additional_claims,
        expires_delta=timedelta(minutes=15)
    )
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 900
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user data.
    
    Returns:
        - user: Current user data
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user_schema.dump(user)), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for current user.
    
    Request Body:
        - current_password: Current password
        - new_password: New password
        - confirm_password: Password confirmation
        
    Returns:
        - message: Success message
    """
    try:
        data = ChangePasswordSchema().load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Verify passwords match
    if data['new_password'] != data['confirm_password']:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    # Update password
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint (client should delete tokens).
    
    Returns:
        - message: Success message
    """
    # In a production system, add token to blacklist
    # For now, client-side token deletion is sufficient
    
    return jsonify({'message': 'Logged out successfully'}), 200
