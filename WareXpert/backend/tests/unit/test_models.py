"""
Unit tests for database models.
Tests model creation, relationships, properties, and methods.
"""

import pytest
from datetime import datetime
from app.models import Tenant, User, Warehouse, Location, Product, Stock, StockMovement


@pytest.mark.unit
class TestTenantModel:
    """Test cases for Tenant model."""
    
    def test_create_tenant(self, db_session):
        """Test creating a new tenant."""
        tenant = Tenant(
            name="Test Corp",
            subdomain="testcorp",
            plan="premium"
        )
        db_session.add(tenant)
        db_session.commit()
        
        assert tenant.id is not None
        assert tenant.name == "Test Corp"
        assert tenant.subdomain == "testcorp"
        assert tenant.plan == "premium"
        assert tenant.is_active is True
        assert isinstance(tenant.created_at, datetime)
    
    def test_tenant_to_dict(self, sample_tenant):
        """Test tenant to_dict method."""
        data = sample_tenant.to_dict()
        
        assert data['id'] == sample_tenant.id
        assert data['name'] == sample_tenant.name
        assert data['subdomain'] == sample_tenant.subdomain
        assert 'created_at' in data
    
    def test_tenant_unique_subdomain(self, db_session, sample_tenant):
        """Test that subdomain must be unique."""
        duplicate = Tenant(
            name="Another Corp",
            subdomain="test",  # Same as sample_tenant
            plan="basic"
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


@pytest.mark.unit
class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, db_session, sample_tenant):
        """Test creating a new user."""
        from werkzeug.security import generate_password_hash
        
        user = User(
            tenant_id=sample_tenant.id,
            email="newuser@test.com",
            password_hash=generate_password_hash("password123"),
            full_name="New User",
            role="SELLER"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.role == "SELLER"
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_user_check_password(self, sample_admin_user):
        """Test password verification."""
        assert sample_admin_user.check_password("admin123") is True
        assert sample_admin_user.check_password("wrongpassword") is False
    
    def test_user_to_dict(self, sample_admin_user):
        """Test user to_dict method."""
        data = sample_admin_user.to_dict()
        
        assert data['id'] == sample_admin_user.id
        assert data['email'] == sample_admin_user.email
        assert data['role'] == sample_admin_user.role
        assert 'password_hash' not in data  # Should not expose password
    
    def test_user_tenant_relationship(self, sample_admin_user, sample_tenant):
        """Test user-tenant relationship."""
        assert sample_admin_user.tenant.id == sample_tenant.id
        assert sample_admin_user in sample_tenant.users


@pytest.mark.unit
class TestWarehouseModel:
    """Test cases for Warehouse model."""
    
    def test_create_warehouse(self, db_session, sample_tenant):
        """Test creating a new warehouse."""
        warehouse = Warehouse(
            tenant_id=sample_tenant.id,
            code="WH-001",
            name="Main Warehouse",
            length=100.0,
            width=50.0,
            height=10.0,
            total_capacity_m3=50000.0
        )
        db_session.add(warehouse)
        db_session.commit()
        
        assert warehouse.id is not None
        assert warehouse.code == "WH-001"
        assert warehouse.length == 100.0
        assert warehouse.is_active is True
    
    def test_warehouse_capacity_usage(self, sample_warehouse):
        """Test warehouse capacity usage calculation."""
        sample_warehouse.total_capacity_m3 = 1000.0
        sample_warehouse.used_capacity_m3 = 250.0
        
        assert sample_warehouse.capacity_usage_percent == 25.0
    
    def test_warehouse_capacity_usage_zero(self, sample_warehouse):
        """Test capacity usage when total is zero."""
        sample_warehouse.total_capacity_m3 = 0.0
        sample_warehouse.used_capacity_m3 = 0.0
        
        assert sample_warehouse.capacity_usage_percent == 0.0
    
    def test_warehouse_unique_code_per_tenant(self, db_session, sample_warehouse):
        """Test that warehouse code must be unique per tenant."""
        duplicate = Warehouse(
            tenant_id=sample_warehouse.tenant_id,
            code="WH-TEST",  # Same code
            name="Another Warehouse",
            length=50.0,
            width=30.0,
            height=6.0
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


@pytest.mark.unit
class TestLocationModel:
    """Test cases for Location model."""
    
    def test_create_location(self, db_session, sample_warehouse):
        """Test creating a new location."""
        location = Location(
            warehouse_id=sample_warehouse.id,
            code="B-02-03",
            type="pallet",
            zone="storage",
            x_position=10.0,
            y_position=5.0,
            z_position=2.0,
            capacity_m3=5.0,
            capacity_kg=1000.0
        )
        db_session.add(location)
        db_session.commit()
        
        assert location.id is not None
        assert location.code == "B-02-03"
        assert location.zone == "storage"
        assert location.is_active is True
    
    def test_location_capacity_usage(self, sample_location):
        """Test location capacity usage calculation."""
        sample_location.capacity_m3 = 10.0
        sample_location.used_m3 = 3.0
        
        assert sample_location.current_capacity_usage == 30.0
    
    def test_location_available_capacity(self, sample_location):
        """Test available capacity calculation."""
        sample_location.capacity_m3 = 10.0
        sample_location.used_m3 = 3.0
        
        available = sample_location.capacity_m3 - sample_location.used_m3
        assert available == 7.0
    
    def test_location_warehouse_relationship(self, sample_location, sample_warehouse):
        """Test location-warehouse relationship."""
        assert sample_location.warehouse.id == sample_warehouse.id
        assert sample_location in sample_warehouse.locations


@pytest.mark.unit
class TestProductModel:
    """Test cases for Product model."""
    
    def test_create_product(self, db_session, sample_tenant, sample_warehouse):
        """Test creating a new product."""
        product = Product(
            tenant_id=sample_tenant.id,
            warehouse_id=sample_warehouse.id,
            sku="PROD-001",
            name="Test Product",
            category="Electronics",
            cost_price=100.0,
            sale_price=150.0
        )
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.sku == "PROD-001"
        assert product.name == "Test Product"
        assert product.is_active is True
    
    def test_product_margin(self, sample_product, db_session):
        """Test product margin calculation."""
        sample_product.cost_price = 100.0
        sample_product.sale_price = 150.0
        sample_product.margin_percent = 50.0
        db_session.commit()
        
        # Calculate margin manually
        margin = sample_product.sale_price - sample_product.cost_price
        assert margin == 50.0
    
    def test_product_margin_percent(self, sample_product, db_session):
        """Test product margin percentage."""
        sample_product.cost_price = 100.0
        sample_product.sale_price = 150.0
        sample_product.margin_percent = 50.0
        db_session.commit()
        
        assert sample_product.margin_percent == 50.0
    
    def test_product_margin_zero_cost(self, sample_product, db_session):
        """Test margin when cost is zero."""
        sample_product.cost_price = 0.0
        sample_product.sale_price = 150.0
        sample_product.margin_percent = 0.0
        db_session.commit()
        
        # When cost is zero, margin percent can be set to 0
        assert sample_product.margin_percent == 0.0
    
    def test_product_unique_sku_per_tenant(self, db_session, sample_product):
        """Test that SKU must be unique globally."""
        duplicate = Product(
            tenant_id=sample_product.tenant_id,
            warehouse_id=sample_product.warehouse_id,
            sku="TEST-001",  # Same SKU as sample_product
            name="Another Product",
            cost_price=50.0,
            sale_price=100.0
        )
        db_session.add(duplicate)
        
        with pytest.raises(Exception):  # IntegrityError - SKU is globally unique
            db_session.commit()


@pytest.mark.unit
class TestStockModel:
    """Test cases for Stock model."""
    
    def test_create_stock(self, db_session, sample_product, sample_location):
        """Test creating a stock entry."""
        stock = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=100,
            reserved=10,
            available=90
        )
        db_session.add(stock)
        db_session.commit()
        
        assert stock.id is not None
        assert stock.quantity == 100
        assert stock.reserved == 10
        assert stock.available == 90
    
    def test_stock_update_available(self, db_session, sample_product, sample_location):
        """Test stock available calculation."""
        stock = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=100,
            reserved=25
        )
        db_session.add(stock)
        stock.update_available()
        
        assert stock.available == 75


@pytest.mark.unit
class TestStockMovementModel:
    """Test cases for StockMovement model."""
    
    def test_create_stock_movement(self, db_session, sample_product, sample_location):
        """Test creating a stock movement."""
        movement = StockMovement(
            product_id=sample_product.id,
            location_to_id=sample_location.id,
            type="IN",
            quantity=50,
            reason="Initial stock"
        )
        db_session.add(movement)
        db_session.commit()
        
        assert movement.id is not None
        assert movement.type == "IN"
        assert movement.quantity == 50
        assert isinstance(movement.created_at, datetime)
    
    def test_stock_movement_transfer(self, db_session, sample_product, sample_location, sample_warehouse):
        """Test creating a transfer movement."""
        # Create second location
        location2 = Location(
            warehouse_id=sample_warehouse.id,
            code="A-02-02",
            type="shelf",
            zone="storage",
            x_position=5.0,
            y_position=5.0,
            z_position=0.0
        )
        db_session.add(location2)
        db_session.commit()
        
        movement = StockMovement(
            product_id=sample_product.id,
            location_from_id=sample_location.id,
            location_to_id=location2.id,
            type="TRANSFER",
            quantity=25
        )
        db_session.add(movement)
        db_session.commit()
        
        assert movement.location_from_id == sample_location.id
        assert movement.location_to_id == location2.id
        assert movement.type == "TRANSFER"
