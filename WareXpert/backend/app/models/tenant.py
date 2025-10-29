"""
Tenant Model
Multi-tenancy support - each client is a tenant
"""

from datetime import datetime
from app import db

class Tenant(db.Model):
    """
    Tenant/Client company
    Each tenant has isolated data (multi-tenancy)
    """
    __tablename__ = 'tenants'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Identification
    name = db.Column(db.String(200), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=False)
    
    # Business Info
    tax_id = db.Column(db.String(50))  # RUT in Chile
    address = db.Column(db.String(500))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    
    # Subscription
    plan = db.Column(db.String(50), default='free')  # free, basic, premium, enterprise
    is_active = db.Column(db.Boolean, default=True)
    
    # Branding
    logo_url = db.Column(db.String(500))
    primary_color = db.Column(db.String(7), default='#1976d2')  # Hex color
    
    # Settings (JSON)
    settings = db.Column(db.JSON, default={})
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    warehouses = db.relationship('Warehouse', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='tenant', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'tax_id': self.tax_id,
            'plan': self.plan,
            'is_active': self.is_active,
            'logo_url': self.logo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
