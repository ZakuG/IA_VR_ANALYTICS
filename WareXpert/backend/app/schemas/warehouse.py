"""Warehouse and Location schemas for API serialization and validation."""
from marshmallow import fields, validate, validates, ValidationError
from app.schemas import BaseSchema, TimestampSchema


class LocationSchema(TimestampSchema):
    """Schema for warehouse location."""
    id = fields.Integer(dump_only=True)
    warehouse_id = fields.Integer(required=True)
    code = fields.String(required=True, validate=validate.Length(max=50))
    type = fields.String(
        required=True,
        validate=validate.OneOf(['SHELF', 'RACK', 'FLOOR', 'PALLET', 'BIN'])
    )
    zone = fields.String(
        required=True,
        validate=validate.OneOf(['PICKING', 'STORAGE', 'RECEIVING', 'SHIPPING'])
    )
    
    # 3D Position
    position_x = fields.Float(required=True, validate=validate.Range(min=0))
    position_y = fields.Float(required=True, validate=validate.Range(min=0))
    position_z = fields.Float(required=True, validate=validate.Range(min=0))
    
    # Dimensions
    length_m = fields.Float(required=True, validate=validate.Range(min=0.01))
    width_m = fields.Float(required=True, validate=validate.Range(min=0.01))
    height_m = fields.Float(required=True, validate=validate.Range(min=0.01))
    
    # Capacity
    max_capacity_m3 = fields.Float(required=True, validate=validate.Range(min=0))
    max_capacity_kg = fields.Float(required=True, validate=validate.Range(min=0))
    max_items = fields.Integer(required=True, validate=validate.Range(min=1))
    
    # Current usage
    current_capacity_m3 = fields.Float(dump_only=True)
    current_capacity_kg = fields.Float(dump_only=True)
    current_items = fields.Integer(dump_only=True)
    
    # Metadata
    priority_level = fields.Integer(
        missing=5,
        validate=validate.Range(min=1, max=10)
    )
    is_active = fields.Boolean(missing=True)
    notes = fields.String(allow_none=True)
    
    # Calculated fields
    current_capacity_usage = fields.Float(dump_only=True)
    is_full = fields.Boolean(dump_only=True)


class LocationCreateSchema(BaseSchema):
    """Schema for creating a new location."""
    code = fields.String(required=True, validate=validate.Length(max=50))
    type = fields.String(allow_none=True, validate=validate.Length(max=50))
    zone = fields.String(allow_none=True, validate=validate.Length(max=50))
    
    # 3D Position - match model field names
    x_position = fields.Float(required=True, validate=validate.Range(min=0))
    y_position = fields.Float(required=True, validate=validate.Range(min=0))
    z_position = fields.Float(required=True, validate=validate.Range(min=0))
    
    # Dimensions (optional) - no _m suffix
    length = fields.Float(allow_none=True, validate=validate.Range(min=0))
    width = fields.Float(allow_none=True, validate=validate.Range(min=0))
    height = fields.Float(allow_none=True, validate=validate.Range(min=0))
    
    # Capacities - match model field names
    capacity_m3 = fields.Float(allow_none=True, validate=validate.Range(min=0))
    capacity_kg = fields.Float(allow_none=True, validate=validate.Range(min=0))
    max_stackable = fields.Integer(allow_none=True, validate=validate.Range(min=1))
    
    priority_level = fields.Integer(missing=5, validate=validate.Range(min=1, max=10))
    notes = fields.String(allow_none=True)


class LocationUpdateSchema(BaseSchema):
    """Schema for updating location data."""
    code = fields.String(validate=validate.Length(max=50))
    type = fields.String(
        validate=validate.OneOf(['SHELF', 'RACK', 'FLOOR', 'PALLET', 'BIN'])
    )
    zone = fields.String(
        validate=validate.OneOf(['PICKING', 'STORAGE', 'RECEIVING', 'SHIPPING'])
    )
    position_x = fields.Float(validate=validate.Range(min=0))
    position_y = fields.Float(validate=validate.Range(min=0))
    position_z = fields.Float(validate=validate.Range(min=0))
    length_m = fields.Float(validate=validate.Range(min=0.01))
    width_m = fields.Float(validate=validate.Range(min=0.01))
    height_m = fields.Float(validate=validate.Range(min=0.01))
    max_capacity_m3 = fields.Float(validate=validate.Range(min=0))
    max_capacity_kg = fields.Float(validate=validate.Range(min=0))
    max_items = fields.Integer(validate=validate.Range(min=1))
    priority_level = fields.Integer(validate=validate.Range(min=1, max=10))
    is_active = fields.Boolean()
    notes = fields.String(allow_none=True)


class WarehouseSchema(TimestampSchema):
    """Schema for warehouse."""
    id = fields.Integer(dump_only=True)
    tenant_id = fields.Integer(dump_only=True)
    code = fields.String(required=True, validate=validate.Length(max=50))
    name = fields.String(required=True, validate=validate.Length(max=255))
    
    # Dimensions (meters)
    length = fields.Float(required=True, validate=validate.Range(min=0))  # Changed from length_m
    width = fields.Float(required=True, validate=validate.Range(min=0))   # Changed from width_m
    height = fields.Float(required=True, validate=validate.Range(min=0))  # Changed from height_m
    
    # Capacity
    total_capacity_m3 = fields.Float(required=True, validate=validate.Range(min=0))
    total_capacity_kg = fields.Float(required=True, validate=validate.Range(min=0))
    total_capacity_items = fields.Integer(required=True, validate=validate.Range(min=0))
    
    # Current usage
    used_capacity_m3 = fields.Float(dump_only=True)
    used_capacity_kg = fields.Float(dump_only=True)
    used_capacity_items = fields.Integer(dump_only=True)
    
    # Metadata
    is_active = fields.Boolean(missing=True)
    timezone = fields.String(missing='America/Santiago')
    
    # Calculated fields
    capacity_usage_percent = fields.Float(dump_only=True)
    available_capacity_m3 = fields.Float(dump_only=True)
    
    # Nested relationships
    locations = fields.Nested(LocationSchema, many=True, dump_only=True)
    location_count = fields.Integer(dump_only=True)


class WarehouseCreateSchema(BaseSchema):
    """Schema for creating a new warehouse."""
    code = fields.String(required=True, validate=validate.Length(max=50))
    name = fields.String(required=True, validate=validate.Length(max=255))
    
    # Dimensions (meters) - match model field names
    length = fields.Float(required=True, validate=validate.Range(min=0))
    width = fields.Float(required=True, validate=validate.Range(min=0))
    height = fields.Float(required=True, validate=validate.Range(min=0))
    
    # Capacities
    total_capacity_m3 = fields.Float(required=True, validate=validate.Range(min=0))
    total_capacity_kg = fields.Float(required=True, validate=validate.Range(min=0))
    total_capacity_items = fields.Integer(required=True, validate=validate.Range(min=0))


class WarehouseUpdateSchema(BaseSchema):
    """Schema for updating warehouse data."""
    code = fields.String(validate=validate.Length(max=50))
    name = fields.String(validate=validate.Length(max=255))
    description = fields.String(allow_none=True)
    address = fields.String(validate=validate.Length(max=500))
    city = fields.String(validate=validate.Length(max=100))
    state = fields.String(allow_none=True, validate=validate.Length(max=100))
    country = fields.String(validate=validate.Length(max=100))
    postal_code = fields.String(allow_none=True, validate=validate.Length(max=20))
    phone = fields.String(allow_none=True, validate=validate.Length(max=20))
    email = fields.Email(allow_none=True)
    manager_name = fields.String(allow_none=True, validate=validate.Length(max=255))
    length_m = fields.Float(validate=validate.Range(min=1))
    width_m = fields.Float(validate=validate.Range(min=1))
    height_m = fields.Float(validate=validate.Range(min=1))
    total_capacity_m3 = fields.Float(validate=validate.Range(min=0))
    total_capacity_kg = fields.Float(validate=validate.Range(min=0))
    total_capacity_items = fields.Integer(validate=validate.Range(min=0))
    is_active = fields.Boolean()
    timezone = fields.String()


class WarehouseListQuerySchema(BaseSchema):
    """Schema for warehouse list query parameters."""
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    search = fields.String(allow_none=True)
    is_active = fields.Boolean(allow_none=True)
    city = fields.String(allow_none=True)
    sort_by = fields.String(
        missing='created_at',
        validate=validate.OneOf(['created_at', 'name', 'code', 'capacity_usage_percent'])
    )
    sort_order = fields.String(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )
