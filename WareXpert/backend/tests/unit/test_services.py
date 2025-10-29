"""
Unit tests for Service layer.
Tests business logic and service methods.
"""

import pytest
from decimal import Decimal
from app.services.warehouse import WarehouseService
from app.services.product import ProductService
from app.models import Warehouse, Location, Product


@pytest.mark.unit
class TestWarehouseService:
    """Test cases for WarehouseService."""
    
    def test_create_warehouse(self, db_session, sample_tenant):
        """Test creating a new warehouse."""
        service = WarehouseService()
        
        warehouse_data = {
            'code': 'WH-SERVICE-001',
            'name': 'Service Test Warehouse',
            'address': '123 Service St',
            'city': 'Santiago',
            'country': 'Chile',
            'length_m': 100.0,
            'width_m': 50.0,
            'height_m': 10.0,
            'total_capacity_m3': 50000.0,
            'total_capacity_kg': 1000000.0,
            'total_capacity_items': 10000
        }
        
        warehouse = service.create_warehouse(
            tenant_id=sample_tenant.id,
            user_id=1,
            **warehouse_data
        )
        
        assert warehouse is not None
        assert warehouse.code == 'WH-SERVICE-001'
        assert warehouse.tenant_id == sample_tenant.id
    
    def test_update_warehouse(self, db_session, sample_warehouse):
        """Test updating warehouse data."""
        service = WarehouseService()
        
        updated = service.update_warehouse(
            warehouse_id=sample_warehouse.id,
            tenant_id=sample_warehouse.tenant_id,
            user_id=1,
            name='Updated Warehouse Name',
            is_active=False
        )
        
        assert updated.name == 'Updated Warehouse Name'
        assert updated.is_active is False
    
    def test_get_warehouse_stats(self, db_session, sample_warehouse, sample_location):
        """Test getting warehouse statistics."""
        service = WarehouseService()
        
        stats = service.get_warehouse_stats(
            warehouse_id=sample_warehouse.id,
            tenant_id=sample_warehouse.tenant_id
        )
        
        assert stats is not None
        assert 'total_locations' in stats
        assert 'capacity' in stats
    
    def test_delete_warehouse(self, db_session, sample_tenant):
        """Test deleting a warehouse."""
        service = WarehouseService()
        
        # Create warehouse to delete
        warehouse = Warehouse(
            tenant_id=sample_tenant.id,
            code='WH-TO-DELETE',
            name='To Delete',
            length=50.0,
            width=30.0,
            height=6.0,
            total_capacity_m3=9000.0,
            total_capacity_kg=500000.0,
            total_capacity_items=5000
        )
        db_session.add(warehouse)
        db_session.commit()
        
        result = service.delete_warehouse(
            warehouse_id=warehouse.id,
            tenant_id=sample_tenant.id,
            user_id=1
        )
        
        assert result is True


@pytest.mark.unit
class TestProductService:
    """Test cases for ProductService."""
    
    def test_create_product(self, db_session, sample_warehouse, sample_tenant):
        """Test creating a new product."""
        service = ProductService()
        
        product_data = {
            'sku': 'PROD-SERVICE-001',
            'name': 'Service Test Product',
            'warehouse_id': sample_warehouse.id,
            'cost_price': Decimal('50.00'),
            'sale_price': Decimal('100.00'),
            'weight_kg': 1.0,
            'volume_m3': 0.01,
            'category': 'Test'
        }
        
        product = service.create_product(
            tenant_id=sample_tenant.id,
            user_id=1,
            **product_data
        )
        
        assert product is not None
        assert product.sku == 'PROD-SERVICE-001'
        assert product.warehouse_id == sample_warehouse.id
    
    def test_update_product(self, db_session, sample_product):
        """Test updating product data."""
        service = ProductService()
        
        updated = service.update_product(
            product_id=sample_product.id,
            tenant_id=sample_product.tenant_id,
            user_id=1,
            name='Updated Product Name',
            sale_price=Decimal('250.00')
        )
        
        assert updated.name == 'Updated Product Name'
        assert updated.sale_price == Decimal('250.00')
    
    def test_get_product_details(self, db_session, sample_product):
        """Test getting product details."""
        service = ProductService()
        
        product = service.get_product(
            product_id=sample_product.id,
            tenant_id=sample_product.tenant_id
        )
        
        assert product is not None
        assert product.id == sample_product.id
        assert product.sku == sample_product.sku
    
    def test_list_products_paginated(self, db_session, sample_product):
        """Test listing products with pagination."""
        service = ProductService()
        
        result = service.get_products(
            tenant_id=sample_product.tenant_id,
            page=1,
            per_page=20
        )
        
        assert result is not None
        assert 'items' in result
        assert 'total' in result
        assert len(result['items']) > 0
