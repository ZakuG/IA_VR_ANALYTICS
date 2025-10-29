"""
Warehouse Models
Warehouse and Location models for physical space management
"""

from datetime import datetime
from app import db

class Warehouse(db.Model):
    """
    Physical warehouse/bodega
    Contains locations where products are stored
    """
    __tablename__ = 'warehouses'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Identification
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    
    # Physical Dimensions (meters)
    length = db.Column(db.Float, nullable=False)  # Largo
    width = db.Column(db.Float, nullable=False)   # Ancho
    height = db.Column(db.Float, nullable=False)  # Alto
    
    # Total Capacities
    total_capacity_m3 = db.Column(db.Float)       # Volume
    total_capacity_kg = db.Column(db.Float)       # Weight
    total_capacity_items = db.Column(db.Integer)  # Max items
    
    # Used Capacities (calculated)
    used_capacity_m3 = db.Column(db.Float, default=0.0)
    used_capacity_kg = db.Column(db.Float, default=0.0)
    used_capacity_items = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    locations = db.relationship('Location', backref='warehouse', lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='warehouse', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_warehouse_tenant', 'tenant_id'),
        db.UniqueConstraint('tenant_id', 'code', name='uq_warehouse_code_per_tenant'),
    )
    
    @property
    def capacity_usage_percent(self):
        """Calculate percentage of capacity used (by volume)"""
        if not self.total_capacity_m3 or self.total_capacity_m3 == 0:
            return 0
        return (self.used_capacity_m3 / self.total_capacity_m3) * 100
    
    @property
    def available_capacity_m3(self):
        """Calculate available capacity in m3"""
        if not self.total_capacity_m3:
            return 0
        return self.total_capacity_m3 - self.used_capacity_m3
    
    def __repr__(self):
        return f'<Warehouse {self.code} - {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'code': self.code,
            'name': self.name,
            'dimensions': {
                'length': self.length,
                'width': self.width,
                'height': self.height
            },
            'capacity': {
                'total_m3': self.total_capacity_m3,
                'total_kg': self.total_capacity_kg,
                'total_items': self.total_capacity_items,
                'used_m3': self.used_capacity_m3,
                'used_kg': self.used_capacity_kg,
                'used_items': self.used_capacity_items,
                'usage_percent': round(self.capacity_usage_percent, 2),
                'available_m3': round(self.available_capacity_m3, 2)
            },
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Location(db.Model):
    """
    Storage location within warehouse
    Can be shelf, rack, floor space, bin, etc.
    """
    __tablename__ = 'locations'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    
    # Identification
    code = db.Column(db.String(50), nullable=False)  # e.g., "A-03-02"
    
    # Type and Zone
    type = db.Column(db.String(50))  # shelf, rack, floor, pallet, bin
    zone = db.Column(db.String(50))  # picking, storage, receiving, shipping, quarantine
    
    # 3D Position (meters from origin)
    x_position = db.Column(db.Float, nullable=False)
    y_position = db.Column(db.Float, nullable=False)
    z_position = db.Column(db.Float, nullable=False)
    
    # Dimensions (meters)
    length = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    
    # Capacities
    capacity_m3 = db.Column(db.Float)              # Volume
    capacity_kg = db.Column(db.Float)              # Max weight
    max_stackable = db.Column(db.Integer)          # Max units of same product
    
    # Current Usage (calculated)
    used_m3 = db.Column(db.Float, default=0.0)
    used_kg = db.Column(db.Float, default=0.0)
    current_items = db.Column(db.Integer, default=0)
    
    # Priority (for automatic assignment)
    priority_level = db.Column(db.Integer, default=5)  # 1=high, 10=low
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_accessible = db.Column(db.Boolean, default=True)  # Accessible for picking
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    stocks = db.relationship('Stock', backref='location', lazy='dynamic', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_location_warehouse', 'warehouse_id'),
        db.Index('idx_location_zone', 'zone'),
        db.UniqueConstraint('warehouse_id', 'code', name='uq_location_code_per_warehouse'),
    )
    
    @property
    def current_capacity_usage(self):
        """Calculate current capacity usage percentage"""
        if self.capacity_m3 == 0:
            return 0
        return (self.used_m3 / self.capacity_m3) * 100
    
    @property
    def is_full(self):
        """Check if location is full (>95% capacity)"""
        return self.current_capacity_usage >= 95
    
    @property
    def available_m3(self):
        """Calculate available volume"""
        return self.capacity_m3 - self.used_m3 if self.capacity_m3 else 0
    
    def __repr__(self):
        return f'<Location {self.code}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'warehouse_id': self.warehouse_id,
            'code': self.code,
            'type': self.type,
            'zone': self.zone,
            'position': {
                'x': self.x_position,
                'y': self.y_position,
                'z': self.z_position
            },
            'dimensions': {
                'length': self.length,
                'width': self.width,
                'height': self.height
            },
            'capacity': {
                'max_m3': self.capacity_m3,
                'max_kg': self.capacity_kg,
                'max_stackable': self.max_stackable,
                'used_m3': self.used_m3,
                'used_kg': self.used_kg,
                'current_items': self.current_items,
                'usage_percent': round(self.current_capacity_usage, 2),
                'available_m3': round(self.available_m3, 2),
                'is_full': self.is_full
            },
            'priority_level': self.priority_level,
            'is_active': self.is_active,
            'is_accessible': self.is_accessible,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
