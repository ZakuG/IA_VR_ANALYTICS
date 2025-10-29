"""Product and Stock schemas for API serialization and validation."""
from marshmallow import fields, validate, validates, ValidationError
from app.schemas import BaseSchema, TimestampSchema


class StockSchema(BaseSchema):
    """Schema for stock in a location."""
    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(required=True)
    location_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=0))
    reserved = fields.Integer(missing=0, validate=validate.Range(min=0))
    available = fields.Integer(dump_only=True)
    location_code = fields.String(dump_only=True)
    location_zone = fields.String(dump_only=True)


class ProductImageSchema(BaseSchema):
    """Schema for product images."""
    image_url = fields.URL(allow_none=True)
    thumbnail_url = fields.URL(allow_none=True)
    gallery = fields.List(fields.URL(), missing=list)


class ProductSchema(TimestampSchema):
    """Schema for product."""
    id = fields.Integer(dump_only=True)
    tenant_id = fields.Integer(dump_only=True)
    warehouse_id = fields.Integer(required=True)
    
    # Identifiers
    sku = fields.String(required=True, validate=validate.Length(max=100))
    barcode = fields.String(allow_none=True, validate=validate.Length(max=100))
    qr_code = fields.String(dump_only=True)  # Auto-generated
    
    # Basic info
    name = fields.String(required=True, validate=validate.Length(max=255))
    description = fields.String(allow_none=True)
    category = fields.String(allow_none=True, validate=validate.Length(max=100))
    brand = fields.String(allow_none=True, validate=validate.Length(max=100))
    
    # Physical properties
    weight_kg = fields.Float(required=True, validate=validate.Range(min=0))
    volume_m3 = fields.Float(required=True, validate=validate.Range(min=0))
    length_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    width_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    height_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    
    # Images
    image_url = fields.URL(allow_none=True)
    thumbnail_url = fields.URL(allow_none=True)
    gallery = fields.List(fields.URL(), missing=list)
    
    # Pricing
    cost_price = fields.Decimal(
        as_string=True,
        places=2,
        required=True,
        validate=validate.Range(min=0)
    )
    sale_price = fields.Decimal(
        as_string=True,
        places=2,
        required=True,
        validate=validate.Range(min=0)
    )
    margin_percent = fields.Float(dump_only=True)
    
    # Inventory levels
    stock_min = fields.Integer(
        missing=0,
        validate=validate.Range(min=0)
    )
    stock_max = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=0)
    )
    reorder_point = fields.Integer(
        missing=0,
        validate=validate.Range(min=0)
    )
    
    # Sales metrics
    total_sales = fields.Integer(dump_only=True)
    last_sale_date = fields.DateTime(dump_only=True, allow_none=True)
    rotation_days = fields.Integer(dump_only=True, allow_none=True)
    
    # Status
    is_active = fields.Boolean(missing=True)
    is_visible_ecommerce = fields.Boolean(missing=False)
    
    # Calculated fields
    total_stock = fields.Integer(dump_only=True)
    available_stock = fields.Integer(dump_only=True)
    
    # Nested relationships
    stock_locations = fields.Nested(StockSchema, many=True, dump_only=True)


class ProductCreateSchema(BaseSchema):
    """Schema for creating a new product."""
    warehouse_id = fields.Integer(required=True)
    sku = fields.String(required=True, validate=validate.Length(max=100))
    barcode = fields.String(allow_none=True, validate=validate.Length(max=100))
    name = fields.String(required=True, validate=validate.Length(max=255))
    description = fields.String(allow_none=True)
    category = fields.String(allow_none=True, validate=validate.Length(max=100))
    brand = fields.String(allow_none=True, validate=validate.Length(max=100))
    weight_kg = fields.Float(required=True, validate=validate.Range(min=0))
    volume_m3 = fields.Float(required=True, validate=validate.Range(min=0))
    length_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    width_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    height_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    cost_price = fields.Decimal(
        as_string=True,
        places=2,
        required=True,
        validate=validate.Range(min=0)
    )
    sale_price = fields.Decimal(
        as_string=True,
        places=2,
        required=True,
        validate=validate.Range(min=0)
    )
    stock_min = fields.Integer(missing=0, validate=validate.Range(min=0))
    stock_max = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    reorder_point = fields.Integer(missing=0, validate=validate.Range(min=0))
    is_visible_ecommerce = fields.Boolean(missing=False)


class ProductUpdateSchema(BaseSchema):
    """Schema for updating product data."""
    warehouse_id = fields.Integer()
    sku = fields.String(validate=validate.Length(max=100))
    barcode = fields.String(allow_none=True, validate=validate.Length(max=100))
    name = fields.String(validate=validate.Length(max=255))
    description = fields.String(allow_none=True)
    category = fields.String(allow_none=True, validate=validate.Length(max=100))
    brand = fields.String(allow_none=True, validate=validate.Length(max=100))
    weight_kg = fields.Float(validate=validate.Range(min=0))
    volume_m3 = fields.Float(validate=validate.Range(min=0))
    length_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    width_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    height_cm = fields.Float(allow_none=True, validate=validate.Range(min=0))
    cost_price = fields.Decimal(
        as_string=True,
        places=2,
        validate=validate.Range(min=0)
    )
    sale_price = fields.Decimal(
        as_string=True,
        places=2,
        validate=validate.Range(min=0)
    )
    stock_min = fields.Integer(validate=validate.Range(min=0))
    stock_max = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    reorder_point = fields.Integer(validate=validate.Range(min=0))
    is_active = fields.Boolean()
    is_visible_ecommerce = fields.Boolean()


class ProductListQuerySchema(BaseSchema):
    """Schema for product list query parameters."""
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))
    search = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    brand = fields.String(allow_none=True)
    warehouse_id = fields.Integer(allow_none=True)
    is_active = fields.Boolean(allow_none=True)
    is_visible_ecommerce = fields.Boolean(allow_none=True)
    min_price = fields.Decimal(as_string=True, allow_none=True)
    max_price = fields.Decimal(as_string=True, allow_none=True)
    low_stock = fields.Boolean(allow_none=True)  # stock < reorder_point
    out_of_stock = fields.Boolean(allow_none=True)  # stock = 0
    sort_by = fields.String(
        missing='created_at',
        validate=validate.OneOf([
            'created_at', 'name', 'sku', 'sale_price', 
            'total_sales', 'total_stock'
        ])
    )
    sort_order = fields.String(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )


class ProductSearchSchema(BaseSchema):
    """Schema for advanced product search."""
    q = fields.String(required=True, validate=validate.Length(min=1))
    filters = fields.Dict(missing=dict)
    page = fields.Integer(missing=1, validate=validate.Range(min=1))
    per_page = fields.Integer(missing=20, validate=validate.Range(min=1, max=100))


class AssignLocationSchema(BaseSchema):
    """Schema for assigning product to location."""
    location_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))


class SuggestLocationResponseSchema(BaseSchema):
    """Schema for location suggestion response."""
    location_id = fields.Integer(required=True)
    location_code = fields.String(required=True)
    score = fields.Float(required=True)
    reasons = fields.List(fields.String(), required=True)
    available_capacity_m3 = fields.Float(required=True)
    zone = fields.String(required=True)
