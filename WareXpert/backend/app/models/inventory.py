"""
Inventory Models
Product, Stock, and StockMovement models for inventory management
"""

from datetime import datetime
from app import db

class Product(db.Model):
    """
    Product/Item in inventory
    Can be spare parts, finished goods, or any sellable item
    """
    __tablename__ = 'products'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    
    # Identification
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(100), index=True)
    qr_code = db.Column(db.String(500))  # URL or data
    
    # Basic Information
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    brand = db.Column(db.String(100), index=True)
    
    # Physical Dimensions
    weight_kg = db.Column(db.Float)
    volume_m3 = db.Column(db.Float)
    length_cm = db.Column(db.Float)
    width_cm = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    
    # Images
    image_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    gallery = db.Column(db.JSON)  # Array of image URLs
    
    # Pricing
    cost_price = db.Column(db.Float)         # Precio de costo
    sale_price = db.Column(db.Float)         # Precio de venta
    margin_percent = db.Column(db.Float)     # Calculated margin %
    
    # Inventory Levels
    stock_min = db.Column(db.Integer, default=0)      # Minimum stock alert
    stock_max = db.Column(db.Integer, default=1000)   # Maximum stock
    reorder_point = db.Column(db.Integer)             # Reorder point
    
    # Custom Attributes (flexible JSON)
    # Example for auto parts: {"vehicle_brand": "Toyota", "vehicle_model": "Corolla", "year": 2020}
    attributes = db.Column(db.JSON)
    
    # Sales Metrics (calculated/updated)
    total_sales = db.Column(db.Integer, default=0)
    sales_last_30d = db.Column(db.Integer, default=0)
    sales_frequency = db.Column(db.Float, default=0.0)  # Sales per day
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_visible_ecommerce = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_sold_at = db.Column(db.DateTime)
    
    # Relationships
    stocks = db.relationship('Stock', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    movements = db.relationship('StockMovement', backref='product', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_product_tenant', 'tenant_id'),
        db.Index('idx_product_category', 'category'),
        db.Index('idx_product_brand', 'brand'),
        db.Index('idx_product_name', 'name'),  # For text search
    )
    
    @property
    def total_stock(self):
        """Calculate total stock across all locations"""
        return sum(stock.quantity for stock in self.stocks)
    
    @property
    def available_stock(self):
        """Calculate available stock (not reserved)"""
        return sum(stock.available for stock in self.stocks)
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum"""
        return self.total_stock <= self.stock_min
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.total_stock == 0
    
    def calculate_margin(self):
        """Calculate and update margin percentage"""
        if self.sale_price and self.cost_price:
            self.margin_percent = ((self.sale_price - self.cost_price) / self.sale_price) * 100
        else:
            self.margin_percent = 0
    
    def __repr__(self):
        return f'<Product {self.sku} - {self.name}>'
    
    def to_dict(self, include_stock=True):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'sku': self.sku,
            'barcode': self.barcode,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'brand': self.brand,
            'dimensions': {
                'weight_kg': self.weight_kg,
                'volume_m3': self.volume_m3,
                'length_cm': self.length_cm,
                'width_cm': self.width_cm,
                'height_cm': self.height_cm
            },
            'images': {
                'main': self.image_url,
                'thumbnail': self.thumbnail_url,
                'gallery': self.gallery or []
            },
            'pricing': {
                'cost': self.cost_price,
                'sale': self.sale_price,
                'margin_percent': round(self.margin_percent, 2) if self.margin_percent else 0
            },
            'qr_code': self.qr_code,
            'attributes': self.attributes or {},
            'is_active': self.is_active,
            'is_visible_ecommerce': self.is_visible_ecommerce,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_stock:
            data['stock'] = {
                'total': self.total_stock,
                'available': self.available_stock,
                'minimum': self.stock_min,
                'is_low_stock': self.is_low_stock,
                'is_out_of_stock': self.is_out_of_stock
            }
        
        return data

class Stock(db.Model):
    """
    Stock quantity of a product at a specific location
    One product can be in multiple locations
    """
    __tablename__ = 'stocks'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    
    # Quantities
    quantity = db.Column(db.Integer, default=0, nullable=False)      # Total in location
    reserved = db.Column(db.Integer, default=0, nullable=False)      # Reserved (pending orders)
    available = db.Column(db.Integer, default=0, nullable=False)     # Available = quantity - reserved
    
    # Timestamps
    last_movement = db.Column(db.DateTime)
    last_count = db.Column(db.DateTime)              # Last physical count
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_stock_product', 'product_id'),
        db.Index('idx_stock_location', 'location_id'),
        db.UniqueConstraint('product_id', 'location_id', name='uq_product_location'),
    )
    
    def update_available(self):
        """Update available quantity"""
        self.available = self.quantity - self.reserved
        if self.available < 0:
            self.available = 0
    
    def __repr__(self):
        return f'<Stock Product:{self.product_id} Location:{self.location_id} Qty:{self.quantity}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'location_id': self.location_id,
            'location_code': self.location.code if self.location else None,
            'quantity': self.quantity,
            'reserved': self.reserved,
            'available': self.available,
            'last_movement': self.last_movement.isoformat() if self.last_movement else None,
            'last_count': self.last_count.isoformat() if self.last_count else None
        }

class StockMovement(db.Model):
    """
    History of all stock movements
    Tracks every IN/OUT/TRANSFER/ADJUSTMENT
    """
    __tablename__ = 'stock_movements'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_from_id = db.Column(db.Integer, db.ForeignKey('locations.id'))  # NULL for IN movements
    location_to_id = db.Column(db.Integer, db.ForeignKey('locations.id'))    # NULL for OUT movements
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Movement Details
    type = db.Column(db.String(50), nullable=False)  # IN, OUT, TRANSFER, ADJUSTMENT, RETURN, LOSS
    quantity = db.Column(db.Integer, nullable=False)
    
    # Reference to related entities
    reference_type = db.Column(db.String(50))  # sale, purchase, picking_order, adjustment
    reference_id = db.Column(db.Integer)       # ID of related entity
    
    # Reason/Notes
    reason = db.Column(db.String(500))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    location_from = db.relationship('Location', foreign_keys=[location_from_id])
    location_to = db.relationship('Location', foreign_keys=[location_to_id])
    user = db.relationship('User')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_movement_product', 'product_id'),
        db.Index('idx_movement_type', 'type'),
        db.Index('idx_movement_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<StockMovement {self.type} Product:{self.product_id} Qty:{self.quantity}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_sku': self.product.sku if self.product else None,
            'product_name': self.product.name if self.product else None,
            'type': self.type,
            'quantity': self.quantity,
            'location_from': {
                'id': self.location_from.id,
                'code': self.location_from.code
            } if self.location_from else None,
            'location_to': {
                'id': self.location_to.id,
                'code': self.location_to.code
            } if self.location_to else None,
            'user': {
                'id': self.user.id,
                'name': self.user.full_name
            } if self.user else None,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
