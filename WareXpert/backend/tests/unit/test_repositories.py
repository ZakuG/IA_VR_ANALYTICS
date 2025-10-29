"""
Unit tests for repository layer.
Tests CRUD operations and query methods.
"""

import pytest
from app.repositories.warehouse import WarehouseRepository, LocationRepository
from app.repositories.product import ProductRepository, StockRepository
from app.models import Warehouse, Location, Product, Stock


@pytest.mark.unit
class TestWarehouseRepository:
    """Test cases for WarehouseRepository."""
    
    def test_get_by_id(self, db_session, sample_warehouse):
        """Test getting warehouse by ID."""
        repo = WarehouseRepository()
        warehouse = repo.get_by_id(sample_warehouse.id)
        
        assert warehouse is not None
        assert warehouse.id == sample_warehouse.id
        assert warehouse.code == sample_warehouse.code
    
    def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent warehouse."""
        repo = WarehouseRepository()
        warehouse = repo.get_by_id(99999)
        
        assert warehouse is None
    
    def test_get_all(self, db_session, sample_warehouse):
        """Test getting all warehouses."""
        repo = WarehouseRepository()
        warehouses = repo.get_all()
        
        assert len(warehouses) >= 1
        assert sample_warehouse in warehouses
    
    def test_create(self, db_session, sample_tenant):
        """Test creating a warehouse."""
        repo = WarehouseRepository()
        warehouse = repo.create({
            'tenant_id': sample_tenant.id,
            'code': 'WH-NEW',
            'name': 'New Warehouse',
            'length': 60.0,
            'width': 40.0,
            'height': 8.0
        })
        
        assert warehouse.id is not None
        assert warehouse.code == 'WH-NEW'
        assert warehouse.name == 'New Warehouse'
    
    def test_update(self, db_session, sample_warehouse):
        """Test updating a warehouse."""
        repo = WarehouseRepository()
        updated = repo.update(sample_warehouse.id, {
            'name': 'Updated Warehouse Name'
        })
        
        assert updated.name == 'Updated Warehouse Name'
        assert updated.code == sample_warehouse.code  # Unchanged
    
    def test_delete(self, db_session, sample_warehouse):
        """Test deleting a warehouse."""
        repo = WarehouseRepository()
        result = repo.delete(sample_warehouse.id)
        
        assert result is True
        assert repo.get_by_id(sample_warehouse.id) is None
    
    def test_get_by_code(self, db_session, sample_warehouse):
        """Test getting warehouse by code."""
        repo = WarehouseRepository()
        warehouse = repo.get_by_code(
            sample_warehouse.tenant_id,
            sample_warehouse.code
        )
        
        assert warehouse is not None
        assert warehouse.code == sample_warehouse.code
    
    def test_get_by_tenant(self, db_session, sample_warehouse, sample_tenant):
        """Test getting warehouses by tenant."""
        repo = WarehouseRepository()
        warehouses = repo.get_by_tenant(sample_tenant.id)
        
        assert len(warehouses) >= 1
        assert all(w.tenant_id == sample_tenant.id for w in warehouses)
    
    def test_search(self, db_session, sample_warehouse):
        """Test searching warehouses."""
        repo = WarehouseRepository()
        results = repo.search('Test')
        
        assert len(results) >= 1
        assert any('Test' in w.name for w in results)


@pytest.mark.unit
class TestLocationRepository:
    """Test cases for LocationRepository."""
    
    def test_get_by_code(self, db_session, sample_location, sample_warehouse):
        """Test getting location by code."""
        repo = LocationRepository()
        location = repo.get_by_code(
            sample_warehouse.id,
            sample_location.code
        )
        
        assert location is not None
        assert location.code == sample_location.code
    
    def test_get_by_warehouse(self, db_session, sample_location, sample_warehouse):
        """Test getting locations by warehouse."""
        repo = LocationRepository()
        locations = repo.get_by_warehouse(sample_warehouse.id)
        
        assert len(locations) >= 1
        assert all(loc.warehouse_id == sample_warehouse.id for loc in locations)
    
    def test_get_by_zone(self, db_session, sample_location, sample_warehouse):
        """Test getting locations by zone."""
        repo = LocationRepository()
        locations = repo.get_by_zone(sample_warehouse.id, 'picking')
        
        assert len(locations) >= 1
        assert all(loc.zone == 'picking' for loc in locations)
    
    def test_get_available(self, db_session, sample_location, sample_warehouse):
        """Test getting available locations."""
        # Ensure location has available capacity
        sample_location.capacity_m3 = 10.0
        sample_location.used_m3 = 3.0
        db_session.commit()
        
        repo = LocationRepository()
        locations = repo.get_available(
            warehouse_id=sample_warehouse.id,
            min_capacity_m3=5.0
        )
        
        assert len(locations) >= 1
        assert all(loc.available_capacity_m3 >= 5.0 for loc in locations)
    
    def test_create_location(self, db_session, sample_warehouse):
        """Test creating a location."""
        repo = LocationRepository()
        location = repo.create({
            'warehouse_id': sample_warehouse.id,
            'code': 'C-01-01',
            'type': 'shelf',
            'zone': 'storage',
            'x_position': 15.0,
            'y_position': 10.0,
            'z_position': 0.0,
            'capacity_m3': 2.0
        })
        
        assert location.id is not None
        assert location.code == 'C-01-01'


@pytest.mark.unit
class TestProductRepository:
    """Test cases for ProductRepository."""
    
    def test_get_by_sku(self, db_session, sample_product, sample_tenant):
        """Test getting product by SKU."""
        repo = ProductRepository()
        product = repo.get_by_sku(sample_tenant.id, sample_product.sku)
        
        assert product is not None
        assert product.sku == sample_product.sku
    
    def test_get_by_barcode(self, db_session, sample_product):
        """Test getting product by barcode."""
        repo = ProductRepository()
        product = repo.get_by_barcode(sample_product.barcode)
        
        assert product is not None
        assert product.barcode == sample_product.barcode
    
    def test_get_by_tenant(self, db_session, sample_product, sample_tenant):
        """Test getting products by tenant."""
        repo = ProductRepository()
        products = repo.get_by_tenant(sample_tenant.id)
        
        assert len(products) >= 1
        assert all(p.tenant_id == sample_tenant.id for p in products)
    
    def test_search_by_name(self, db_session, sample_product):
        """Test searching products by name."""
        repo = ProductRepository()
        products = repo.search(query='Test Product')
        
        assert len(products) >= 1
        assert any('Test' in p.name for p in products)
    
    def test_get_by_category(self, db_session, sample_product):
        """Test getting products by category."""
        repo = ProductRepository()
        products = repo.get_by_category(sample_product.category)
        
        assert len(products) >= 1
        assert all(p.category == sample_product.category for p in products)
    
    def test_get_low_stock(self, db_session, sample_product):
        """Test getting low stock products."""
        # Set product with low stock threshold
        sample_product.reorder_point = 20
        db_session.commit()
        
        repo = ProductRepository()
        products = repo.get_low_stock(sample_product.tenant_id)
        
        # Will be in low stock if total stock < reorder_point
        assert isinstance(products, list)


@pytest.mark.unit
class TestStockRepository:
    """Test cases for StockRepository."""
    
    def test_get_by_product(self, db_session, sample_product, sample_location):
        """Test getting stock by product."""
        # Create stock entry
        stock = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=50,
            reserved=5,
            available=45
        )
        db_session.add(stock)
        db_session.commit()
        
        repo = StockRepository()
        stocks = repo.get_by_product(sample_product.id)
        
        assert len(stocks) >= 1
        assert all(s.product_id == sample_product.id for s in stocks)
    
    def test_get_by_location(self, db_session, sample_product, sample_location):
        """Test getting stock by location."""
        # Create stock entry
        stock = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=50,
            reserved=5,
            available=45
        )
        db_session.add(stock)
        db_session.commit()
        
        repo = StockRepository()
        stocks = repo.get_by_location(sample_location.id)
        
        assert len(stocks) >= 1
        assert all(s.location_id == sample_location.id for s in stocks)
    
    def test_get_total_stock(self, db_session, sample_product, sample_location):
        """Test getting total stock for product."""
        # Create multiple stock entries
        stock1 = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=50,
            reserved=5,
            available=45
        )
        db_session.add(stock1)
        db_session.commit()
        
        repo = StockRepository()
        total = repo.get_total_stock(sample_product.id)
        
        assert total == 50
    
    def test_reserve_stock(self, db_session, sample_product, sample_location):
        """Test reserving stock."""
        # Create stock entry
        stock = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=100,
            reserved=0,
            available=100
        )
        db_session.add(stock)
        db_session.commit()
        
        repo = StockRepository()
        result = repo.reserve_stock(stock.id, 20)
        
        assert result is True
        assert stock.reserved == 20
        assert stock.available == 80
    
    def test_reserve_stock_insufficient(self, db_session, sample_product, sample_location):
        """Test reserving more stock than available."""
        # Create stock entry with limited availability
        stock = Stock(
            product_id=sample_product.id,
            location_id=sample_location.id,
            quantity=100,
            reserved=90,
            available=10
        )
        db_session.add(stock)
        db_session.commit()
        
        repo = StockRepository()
        result = repo.reserve_stock(stock.id, 20)  # Try to reserve more than available
        
        assert result is False
        assert stock.reserved == 90  # Unchanged
        assert stock.available == 10  # Unchanged
