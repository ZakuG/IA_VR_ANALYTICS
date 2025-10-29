"""
Sales Models
Quote, Sale, and PickingOrder models for sales management
"""

from datetime import datetime, timedelta
from app import db

class Quote(db.Model):
    """
    Sales quote/cotización
    Sent to customer before confirming sale
    """
    __tablename__ = 'quotes'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Quote Number (auto-generated: COT-202501-0001)
    number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_tax_id = db.Column(db.String(50))  # RUT/DNI
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(50))
    customer_address = db.Column(db.String(500))
    
    # Pricing
    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)  # Discount amount or percentage
    discount_type = db.Column(db.String(20), default='amount')  # amount or percent
    tax = db.Column(db.Float, default=0.0)  # IVA
    total = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, sent, accepted, rejected, converted, expired
    
    # Validity
    valid_until = db.Column(db.DateTime)
    
    # Additional Info
    notes = db.Column(db.Text)
    payment_terms = db.Column(db.String(500))
    delivery_time = db.Column(db.String(100))
    
    # PDF Generation
    pdf_url = db.Column(db.String(500))
    pdf_generated_at = db.Column(db.DateTime)
    
    # User who created the quote
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('QuoteItem', backref='quote', lazy='dynamic', cascade='all, delete-orphan')
    created_by = db.relationship('User')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_quote_tenant', 'tenant_id'),
        db.Index('idx_quote_status', 'status'),
        db.Index('idx_quote_customer_email', 'customer_email'),
    )
    
    @property
    def is_expired(self):
        """Check if quote has expired"""
        if not self.valid_until:
            return False
        return datetime.utcnow() > self.valid_until
    
    def calculate_totals(self):
        """Calculate quote totals from items"""
        self.subtotal = sum(item.subtotal for item in self.items)
        
        # Apply discount
        if self.discount_type == 'percent':
            discount_amount = self.subtotal * (self.discount / 100)
        else:
            discount_amount = self.discount
        
        base_amount = self.subtotal - discount_amount
        
        # Calculate tax (IVA)
        from flask import current_app
        tax_rate = current_app.config.get('TAX_RATE', 19)
        self.tax = base_amount * (tax_rate / 100)
        
        self.total = base_amount + self.tax
    
    def __repr__(self):
        return f'<Quote {self.number}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'customer': {
                'name': self.customer_name,
                'tax_id': self.customer_tax_id,
                'email': self.customer_email,
                'phone': self.customer_phone,
                'address': self.customer_address
            },
            'totals': {
                'subtotal': round(self.subtotal, 2),
                'discount': round(self.discount, 2),
                'discount_type': self.discount_type,
                'tax': round(self.tax, 2),
                'total': round(self.total, 2)
            },
            'status': self.status,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_expired': self.is_expired,
            'notes': self.notes,
            'payment_terms': self.payment_terms,
            'delivery_time': self.delivery_time,
            'pdf_url': self.pdf_url,
            'created_by': {
                'id': self.created_by.id,
                'name': self.created_by.full_name
            } if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }

class QuoteItem(db.Model):
    """
    Individual item in a quote
    """
    __tablename__ = 'quote_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item Details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    discount_type = db.Column(db.String(20), default='amount')  # amount or percent
    subtotal = db.Column(db.Float, nullable=False)
    
    # Product snapshot (at time of quote creation)
    product_name = db.Column(db.String(300))
    product_sku = db.Column(db.String(100))
    
    # Relationships
    product = db.relationship('Product')
    
    def calculate_subtotal(self):
        """Calculate item subtotal"""
        base = self.quantity * self.unit_price
        
        if self.discount_type == 'percent':
            discount_amount = base * (self.discount / 100)
        else:
            discount_amount = self.discount
        
        self.subtotal = base - discount_amount
    
    def __repr__(self):
        return f'<QuoteItem Quote:{self.quote_id} Product:{self.product_id}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_sku': self.product_sku,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': round(self.unit_price, 2),
            'discount': round(self.discount, 2),
            'discount_type': self.discount_type,
            'subtotal': round(self.subtotal, 2)
        }

class Sale(db.Model):
    """
    Confirmed sale/venta
    Created after quote is accepted or direct sale
    """
    __tablename__ = 'sales'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Sale Number (auto-generated: VTA-202501-0001)
    number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Reference to Quote (if converted from quote)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    
    # Customer Information
    customer_name = db.Column(db.String(200), nullable=False)
    customer_tax_id = db.Column(db.String(50))
    customer_email = db.Column(db.String(100))
    customer_phone = db.Column(db.String(50))
    customer_address = db.Column(db.String(500))
    
    # Pricing
    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    
    # Payment
    payment_method = db.Column(db.String(50))  # cash, card, transfer, check, credit
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, partial, refunded
    paid_amount = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(50), default='pending_picking')  
    # pending_picking, picking_in_progress, ready_to_ship, shipped, delivered, cancelled
    
    # Users
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    quote = db.relationship('Quote')
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic', cascade='all, delete-orphan')
    picking_orders = db.relationship('PickingOrder', backref='sale', lazy='dynamic')
    created_by = db.relationship('User')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_sale_tenant', 'tenant_id'),
        db.Index('idx_sale_status', 'status'),
        db.Index('idx_sale_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Sale {self.number}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'quote_id': self.quote_id,
            'customer': {
                'name': self.customer_name,
                'tax_id': self.customer_tax_id,
                'email': self.customer_email,
                'phone': self.customer_phone,
                'address': self.customer_address
            },
            'totals': {
                'subtotal': round(self.subtotal, 2),
                'discount': round(self.discount, 2),
                'tax': round(self.tax, 2),
                'total': round(self.total, 2)
            },
            'payment': {
                'method': self.payment_method,
                'status': self.payment_status,
                'paid_amount': round(self.paid_amount, 2)
            },
            'status': self.status,
            'created_by': {
                'id': self.created_by.id,
                'name': self.created_by.full_name
            } if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }

class SaleItem(db.Model):
    """
    Individual item in a sale
    """
    __tablename__ = 'sale_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))  # Location to pick from
    
    # Item Details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Product snapshot
    product_name = db.Column(db.String(300))
    product_sku = db.Column(db.String(100))
    
    # Picking status
    picked_quantity = db.Column(db.Integer, default=0)
    
    # Relationships
    product = db.relationship('Product')
    location = db.relationship('Location')
    
    def __repr__(self):
        return f'<SaleItem Sale:{self.sale_id} Product:{self.product_id}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_sku': self.product_sku,
            'product_name': self.product_name,
            'location': {
                'id': self.location.id,
                'code': self.location.code
            } if self.location else None,
            'quantity': self.quantity,
            'unit_price': round(self.unit_price, 2),
            'discount': round(self.discount, 2),
            'subtotal': round(self.subtotal, 2),
            'picked_quantity': self.picked_quantity
        }

class PickingOrder(db.Model):
    """
    Picking order for warehouse workers
    Generated after sale is confirmed
    """
    __tablename__ = 'picking_orders'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Picking Order Number (auto-generated: PICK-202501-0001)
    number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Foreign Keys
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Warehouse worker
    
    # Status
    status = db.Column(db.String(50), default='pending')  
    # pending, in_progress, completed, cancelled
    
    # Priority
    priority = db.Column(db.String(50), default='normal')  # urgent, high, normal, low
    
    # Route optimization (JSON)
    route = db.Column(db.JSON)  # Optimized route through warehouse
    
    # Timing
    estimated_time_minutes = db.Column(db.Integer)  # Estimated picking time
    actual_time_minutes = db.Column(db.Integer)     # Actual time taken
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('PickingOrderItem', backref='picking_order', lazy='dynamic', cascade='all, delete-orphan')
    assigned_to = db.relationship('User')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_picking_status', 'status'),
        db.Index('idx_picking_assigned', 'assigned_to_id'),
    )
    
    @property
    def efficiency_score(self):
        """Calculate efficiency (actual time vs estimated)"""
        if not self.actual_time_minutes or not self.estimated_time_minutes:
            return None
        return (self.estimated_time_minutes / self.actual_time_minutes) * 100
    
    def __repr__(self):
        return f'<PickingOrder {self.number}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'number': self.number,
            'sale_id': self.sale_id,
            'assigned_to': {
                'id': self.assigned_to.id,
                'name': self.assigned_to.full_name
            } if self.assigned_to else None,
            'status': self.status,
            'priority': self.priority,
            'route': self.route,
            'timing': {
                'estimated_minutes': self.estimated_time_minutes,
                'actual_minutes': self.actual_time_minutes,
                'efficiency_score': round(self.efficiency_score, 2) if self.efficiency_score else None
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class PickingOrderItem(db.Model):
    """
    Individual item in a picking order
    """
    __tablename__ = 'picking_order_items'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    picking_order_id = db.Column(db.Integer, db.ForeignKey('picking_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    
    # Picking Details
    quantity_required = db.Column(db.Integer, nullable=False)
    quantity_picked = db.Column(db.Integer, default=0)
    
    # Order in route
    sequence = db.Column(db.Integer)  # Order to pick (optimized route)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, picked, not_found, partial
    
    # Notes (if product not found or issue)
    notes = db.Column(db.String(500))
    
    # Timestamp
    picked_at = db.Column(db.DateTime)
    
    # Relationships
    product = db.relationship('Product')
    location = db.relationship('Location')
    
    def __repr__(self):
        return f'<PickingOrderItem Order:{self.picking_order_id} Product:{self.product_id}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'product': {
                'id': self.product.id,
                'sku': self.product.sku,
                'name': self.product.name,
                'image_url': self.product.thumbnail_url
            } if self.product else None,
            'location': {
                'id': self.location.id,
                'code': self.location.code,
                'position': {
                    'x': self.location.x_position,
                    'y': self.location.y_position,
                    'z': self.location.z_position
                }
            } if self.location else None,
            'quantity_required': self.quantity_required,
            'quantity_picked': self.quantity_picked,
            'sequence': self.sequence,
            'status': self.status,
            'notes': self.notes,
            'picked_at': self.picked_at.isoformat() if self.picked_at else None
        }
