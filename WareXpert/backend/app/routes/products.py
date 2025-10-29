"""Product API routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError
from app.services.product import ProductService
from app.schemas.product import (
    ProductSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductListQuerySchema,
    AssignLocationSchema,
    SuggestLocationResponseSchema
)

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

# Service instance
product_service = ProductService()

# Schema instances
product_schema = ProductSchema()
product_list_schema = ProductSchema(many=True)
product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
product_query_schema = ProductListQuerySchema()
assign_location_schema = AssignLocationSchema()
suggest_location_schema = SuggestLocationResponseSchema(many=True)


@products_bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    """List all products with filtering and pagination."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        query_params = product_query_schema.load(request.args)
        
        products, total = product_service.search_products(
            tenant_id=tenant_id,
            **query_params
        )
        
        page = query_params.get('page', 1)
        per_page = query_params.get('per_page', 20)
        pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'items': product_list_schema.dump(products),
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'has_prev': page > 1,
            'has_next': page < pages
        }), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product with auto-generated QR code."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = product_create_schema.load(request.json)
        product = product_service.create_product(tenant_id, data)
        
        return jsonify(product_schema.dump(product)), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get product by ID with stock summary."""
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    product = product_service.get_product(product_id, tenant_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product_schema.dump(product)), 200


@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update product."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        data = product_update_schema.load(request.json)
        product = product_service.update_product(product_id, tenant_id, data)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product_schema.dump(product)), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product."""
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    success = product_service.delete_product(product_id, tenant_id)
    
    if not success:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify({'message': 'Product deleted successfully'}), 200


@products_bp.route('/<int:product_id>/assign-location', methods=['POST'])
@jwt_required()
def assign_location(product_id):
    """Assign product to a location."""
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        user_id = get_jwt()['sub']
        
        data = assign_location_schema.load(request.json)
        
        result = product_service.assign_to_location(
            product_id=product_id,
            tenant_id=tenant_id,
            location_id=data['location_id'],
            quantity=data['quantity'],
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except ValidationError as err:
        return jsonify({'error': err.messages[0] if isinstance(err.messages, list) else err.messages}), 400


@products_bp.route('/<int:product_id>/suggest-locations', methods=['GET'])
@jwt_required()
def suggest_locations(product_id):
    """Get suggested locations for a product."""
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    quantity = request.args.get('quantity', 1, type=int)
    limit = request.args.get('limit', 3, type=int)
    
    suggestions = product_service.suggest_locations(
        product_id=product_id,
        tenant_id=tenant_id,
        quantity=quantity,
        limit=limit
    )
    
    return jsonify(suggest_location_schema.dump(suggestions)), 200


@products_bp.route('/<int:product_id>/stock-summary', methods=['GET'])
@jwt_required()
def get_stock_summary(product_id):
    """Get stock summary for a product."""
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    summary = product_service.get_product_stock_summary(product_id, tenant_id)
    
    if not summary:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(summary), 200
