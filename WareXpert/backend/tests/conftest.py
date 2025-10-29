"""
Test configuration and fixtures for WareXpert backend tests.
This module provides pytest fixtures for database, app, and client setup.
"""

import pytest
import os
from app import create_app, db
from app.models import Tenant, User, Warehouse, Location, Product
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create application for testing with test configuration."""
    # Set testing environment - MUST set TEST_DATABASE_URL before creating app
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TEST_DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['TEST_REDIS_URL'] = 'redis://localhost:6379/15'
    
    # Create app with testing config
    app = create_app('testing')
    
    # Establish application context
    with app.app_context():
        # Create all tables
        db.create_all()
        
        yield app
        
        # Cleanup
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Create a new database session for a test.
    The session is cleared after each test.
    """
    with app.app_context():
        yield db.session
        
        # Cleanup: remove all data after test
        db.session.rollback()
        
        # Clear all tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture(scope='function')
def sample_tenant(db_session):
    """Create a sample tenant for testing."""
    tenant = Tenant(
        name="Test Company",
        subdomain="test",
        plan="premium",
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()  # Commit for tests to use
    return tenant


@pytest.fixture(scope='function')
def sample_admin_user(db_session, sample_tenant):
    """Create a sample admin user for testing."""
    user = User(
        tenant_id=sample_tenant.id,
        email="admin@test.com",
        password_hash=generate_password_hash("admin123"),
        full_name="Test Admin",
        role="ADMIN",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()  # Commit for tests to use
    return user


@pytest.fixture(scope='function')
def sample_seller_user(db_session, sample_tenant):
    """Create a sample seller user for testing."""
    user = User(
        tenant_id=sample_tenant.id,
        email="seller@test.com",
        password_hash=generate_password_hash("seller123"),
        full_name="Test Seller",
        role="SELLER",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()  # Commit for tests to use
    return user


@pytest.fixture(scope='function')
def sample_warehouse(db_session, sample_tenant):
    """Create a sample warehouse for testing."""
    warehouse = Warehouse(
        tenant_id=sample_tenant.id,
        code="WH-TEST",
        name="Test Warehouse",
        length=50.0,
        width=30.0,
        height=6.0,
        total_capacity_m3=9000.0,
        total_capacity_kg=500000.0,
        is_active=True
    )
    db_session.add(warehouse)
    db_session.commit()  # Commit for tests to use
    return warehouse


@pytest.fixture(scope='function')
def sample_location(db_session, sample_warehouse):
    """Create a sample location for testing."""
    location = Location(
        warehouse_id=sample_warehouse.id,
        code="A-01-01",
        type="shelf",
        zone="picking",
        x_position=2.0,
        y_position=2.0,
        z_position=0.0,
        length=1.2,
        width=0.6,
        height=2.0,
        capacity_m3=1.44,  # 1.2 * 0.6 * 2.0
        capacity_kg=500.0,
        max_stackable=100,  # Allow up to 100 items for testing
        is_active=True,
        is_accessible=True
    )
    db_session.add(location)
    db_session.commit()  # Commit for tests to use
    return location


@pytest.fixture(scope='function')
def sample_product(db_session, sample_tenant, sample_warehouse):
    """Create a sample product for testing."""
    product = Product(
        tenant_id=sample_tenant.id,
        warehouse_id=sample_warehouse.id,
        sku="TEST-001",
        name="Test Product",
        description="A product for testing",
        category="Electronics",
        brand="TestBrand",
        barcode="1234567890123",
        length_cm=30.0,
        width_cm=20.0,
        height_cm=10.0,
        weight_kg=0.5,
        volume_m3=0.006,
        cost_price=10.0,
        sale_price=20.0,
        stock_min=5,
        stock_max=100,
        reorder_point=10,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()  # Commit for tests to use
    return product


@pytest.fixture(scope='function')
def auth_headers(client, sample_admin_user):
    """
    Get authentication headers with valid JWT token.
    Login as admin user and return Authorization header.
    """
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    
    data = response.get_json()
    access_token = data['access_token']
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope='function')
def seller_auth_headers(client, sample_seller_user):
    """
    Get authentication headers with seller JWT token.
    Login as seller user and return Authorization header.
    """
    response = client.post('/api/auth/login', json={
        'email': 'seller@test.com',
        'password': 'seller123'
    })
    
    data = response.get_json()
    access_token = data['access_token']
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
