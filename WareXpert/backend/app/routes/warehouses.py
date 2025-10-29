"""Warehouse and Location API routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError
from app.services.warehouse import WarehouseService, LocationService
from app.schemas.warehouse import (
    WarehouseSchema,
    WarehouseCreateSchema,
    WarehouseUpdateSchema,
    WarehouseListQuerySchema,
    LocationSchema,
    LocationCreateSchema,
    LocationUpdateSchema
)

warehouses_bp = Blueprint('warehouses', __name__, url_prefix='/api/warehouses')

# Service instances
warehouse_service = WarehouseService()
location_service = LocationService()

# Schema instances
warehouse_schema = WarehouseSchema()
warehouse_list_schema = WarehouseSchema(many=True)
warehouse_create_schema = WarehouseCreateSchema()
warehouse_update_schema = WarehouseUpdateSchema()
warehouse_query_schema = WarehouseListQuerySchema()

location_schema = LocationSchema()
location_list_schema = LocationSchema(many=True)
location_create_schema = LocationCreateSchema()
location_update_schema = LocationUpdateSchema()


@warehouses_bp.route('', methods=['GET'])
@jwt_required()
def list_warehouses():
    """List all warehouses for current tenant.
    
    Query Parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - search: Search term
        - is_active: Filter by active status
        - city: Filter by city
        - sort_by: Sort field (default: created_at)
        - sort_order: Sort order (asc/desc, default: desc)
        
    Returns:
        - items: List of warehouses
        - total: Total count
        - page: Current page
        - per_page: Items per page
        - pages: Total pages
    """
    try:
        # Get tenant from JWT
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # Parse query parameters
        query_params = warehouse_query_schema.load(request.args)
        
        # Get warehouses
        filters = {}
        if query_params.get('is_active') is not None:
            filters['is_active'] = query_params['is_active']
        if query_params.get('city'):
            filters['city'] = query_params['city']
        
        warehouses, total = warehouse_service.list_warehouses(
            tenant_id=tenant_id,
            page=query_params.get('page', 1),
            per_page=query_params.get('per_page', 20),
            filters=filters,
            sort_by=query_params.get('sort_by', 'created_at'),
            sort_order=query_params.get('sort_order', 'desc')
        )
        
        # Calculate pagination
        page = query_params.get('page', 1)
        per_page = query_params.get('per_page', 20)
        pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'items': warehouse_list_schema.dump(warehouses),
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'has_prev': page > 1,
            'has_next': page < pages
        }), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@warehouses_bp.route('', methods=['POST'])
@jwt_required()
def create_warehouse():
    """Create a new warehouse.
    
    Request Body:
        - code: Warehouse code (unique per tenant)
        - name: Warehouse name
        - address: Street address
        - city: City
        - country: Country
        - length_m, width_m, height_m: Dimensions
        - total_capacity_m3, total_capacity_kg, total_capacity_items: Capacities
        
    Returns:
        - Created warehouse data
    """
    try:
        # Get tenant from JWT
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # Validate request data
        data = warehouse_create_schema.load(request.json)
        
        # Create warehouse
        warehouse = warehouse_service.create_warehouse(tenant_id, data)
        
        return jsonify(warehouse_schema.dump(warehouse)), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@warehouses_bp.route('/<int:warehouse_id>', methods=['GET'])
@jwt_required()
def get_warehouse(warehouse_id):
    """Get warehouse by ID.
    
    Parameters:
        - warehouse_id: Warehouse ID
        
    Returns:
        - Warehouse data with locations
    """
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    warehouse = warehouse_service.get_warehouse(warehouse_id, tenant_id)
    
    if not warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404
    
    return jsonify(warehouse_schema.dump(warehouse)), 200


@warehouses_bp.route('/<int:warehouse_id>', methods=['PUT'])
@jwt_required()
def update_warehouse(warehouse_id):
    """Update warehouse.
    
    Parameters:
        - warehouse_id: Warehouse ID
        
    Request Body:
        - Fields to update (partial update supported)
        
    Returns:
        - Updated warehouse data
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # Validate request data
        data = warehouse_update_schema.load(request.json)
        
        # Update warehouse
        warehouse = warehouse_service.update_warehouse(warehouse_id, tenant_id, data)
        
        if not warehouse:
            return jsonify({'error': 'Warehouse not found'}), 404
        
        return jsonify(warehouse_schema.dump(warehouse)), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@warehouses_bp.route('/<int:warehouse_id>', methods=['DELETE'])
@jwt_required()
def delete_warehouse(warehouse_id):
    """Delete warehouse (soft delete).
    
    Parameters:
        - warehouse_id: Warehouse ID
        
    Returns:
        - Success message
    """
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    success = warehouse_service.delete_warehouse(warehouse_id, tenant_id)
    
    if not success:
        return jsonify({'error': 'Warehouse not found'}), 404
    
    return jsonify({'message': 'Warehouse deleted successfully'}), 200


@warehouses_bp.route('/<int:warehouse_id>/stats', methods=['GET'])
@jwt_required()
def get_warehouse_stats(warehouse_id):
    """Get warehouse statistics.
    
    Parameters:
        - warehouse_id: Warehouse ID
        
    Returns:
        - Statistics data
    """
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    stats = warehouse_service.get_warehouse_stats(warehouse_id, tenant_id)
    
    if not stats:
        return jsonify({'error': 'Warehouse not found'}), 404
    
    return jsonify(stats), 200


# ==================== Location Routes ====================


@warehouses_bp.route('/<int:warehouse_id>/locations', methods=['GET'])
@jwt_required()
def list_locations(warehouse_id):
    """List all locations for a warehouse.
    
    Parameters:
        - warehouse_id: Warehouse ID
        
    Query Parameters:
        - is_active: Filter by active status
        - zone: Filter by zone
        
    Returns:
        - List of locations
    """
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    is_active = request.args.get('is_active')
    if is_active is not None:
        is_active = is_active.lower() == 'true'
    
    zone = request.args.get('zone')
    
    locations = location_service.list_locations(
        warehouse_id=warehouse_id,
        tenant_id=tenant_id,
        is_active=is_active,
        zone=zone
    )
    
    return jsonify(location_list_schema.dump(locations)), 200


@warehouses_bp.route('/<int:warehouse_id>/locations', methods=['POST'])
@jwt_required()
def create_location(warehouse_id):
    """Create a new location in a warehouse.
    
    Parameters:
        - warehouse_id: Warehouse ID
        
    Request Body:
        - code: Location code (unique per warehouse)
        - type: Location type (SHELF, RACK, FLOOR, PALLET, BIN)
        - zone: Zone (PICKING, STORAGE, RECEIVING, SHIPPING)
        - position_x, position_y, position_z: 3D position
        - length_m, width_m, height_m: Dimensions
        - max_capacity_m3, max_capacity_kg, max_items: Capacities
        
    Returns:
        - Created location data
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # Validate request data
        data = location_create_schema.load(request.json)
        
        # Create location
        location = location_service.create_location(warehouse_id, tenant_id, data)
        
        return jsonify(location_schema.dump(location)), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@warehouses_bp.route('/locations/<int:location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    """Get location by ID.
    
    Parameters:
        - location_id: Location ID
        
    Returns:
        - Location data
    """
    claims = get_jwt()
    tenant_id = claims.get('tenant_id')
    
    location = location_service.get_location(location_id, tenant_id)
    
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    
    return jsonify(location_schema.dump(location)), 200


@warehouses_bp.route('/locations/<int:location_id>', methods=['PUT'])
@jwt_required()
def update_location(location_id):
    """Update location.
    
    Parameters:
        - location_id: Location ID
        
    Request Body:
        - Fields to update
        
    Returns:
        - Updated location data
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        # Validate request data
        data = location_update_schema.load(request.json)
        
        # Update location
        location = location_service.update_location(location_id, tenant_id, data)
        
        if not location:
            return jsonify({'error': 'Location not found'}), 404
        
        return jsonify(location_schema.dump(location)), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400


@warehouses_bp.route('/locations/<int:location_id>', methods=['DELETE'])
@jwt_required()
def delete_location(location_id):
    """Delete location (soft delete).
    
    Parameters:
        - location_id: Location ID
        
    Returns:
        - Success message
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        success = location_service.delete_location(location_id, tenant_id)
        
        if not success:
            return jsonify({'error': 'Location not found'}), 404
        
        return jsonify({'message': 'Location deleted successfully'}), 200
        
    except ValidationError as err:
        return jsonify({'error': err.messages[0]}), 400
