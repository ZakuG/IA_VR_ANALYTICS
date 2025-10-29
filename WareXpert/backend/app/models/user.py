"""
User Model
System users with RBAC (Role-Based Access Control)
"""

from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """
    System user
    Each user belongs to one tenant
    """
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Multi-tenancy
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    
    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    avatar_url = db.Column(db.String(500))
    
    # Role-Based Access Control
    role = db.Column(db.String(50), nullable=False, default='VIEWER')
    # Roles: SUPER_ADMIN (100), ADMIN (90), MANAGER (70), SELLER (50), WAREHOUSE (30), VIEWER (10)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_tenant_email', 'tenant_id', 'email'),
    )
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def get_role_score(self):
        """Get numeric score for role (for permission checks)"""
        role_scores = {
            'SUPER_ADMIN': 100,
            'ADMIN': 90,
            'MANAGER': 70,
            'SELLER': 50,
            'WAREHOUSE': 30,
            'VIEWER': 10
        }
        return role_scores.get(self.role, 0)
    
    def has_permission(self, required_role):
        """Check if user has required permission level"""
        role_scores = {
            'SUPER_ADMIN': 100,
            'ADMIN': 90,
            'MANAGER': 70,
            'SELLER': 50,
            'WAREHOUSE': 30,
            'VIEWER': 10
        }
        user_score = self.get_role_score()
        required_score = role_scores.get(required_role, 0)
        return user_score >= required_score
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self, include_sensitive=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['is_verified'] = self.is_verified
        
        return data
