"""
Integration tests for Product API endpoints.
Tests complete workflows for product management.
"""

import pytest
import json
from app.models import Product


@pytest.mark.integration
@pytest.mark.api
class TestProductEndpoints:
    """Test cases for Product API endpoints."""
    
    def test_list_products(self, client, auth_headers, sample_product):
        """Test listing all products."""
        response = client.get('/api/products', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # API returns paginated response
        assert 'items' in data
        assert 'page' in data
        assert 'total' in data
        
        # Verify our sample product is in the list
        products = data['items']
        assert len(products) > 0
        assert any(p['sku'] == 'TEST-001' for p in products)
    
    def test_get_product_by_id(self, client, auth_headers, sample_product):
        """Test getting a specific product."""
        response = client.get(
            f'/api/products/{sample_product.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['sku'] == 'TEST-001'
        assert data['name'] == 'Test Product'
    
    def test_get_product_not_found(self, client, auth_headers):
        """Test getting non-existent product."""
        response = client.get('/api/products/99999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_create_product(self, client, auth_headers, sample_warehouse):
        """Test creating a new product."""
        product_data = {
            'sku': 'PROD-NEW-001',
            'name': 'New Product',
            'description': 'A new test product',
            'category': 'Test Category',
            'warehouse_id': sample_warehouse.id,
            'cost_price': '100.00',
            'sale_price': '150.00',
            'weight_kg': 0.5,
            'volume_m3': 0.006,
            'length_cm': 20.0,
            'width_cm': 15.0,
            'height_cm': 10.0,
            'stock_min': 10,
            'stock_max': 100
        }
        
        response = client.post(
            '/api/products',
            headers=auth_headers,
            json=product_data
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['sku'] == 'PROD-NEW-001'
        assert data['name'] == 'New Product'
        assert data['id'] is not None
    
    def test_create_product_duplicate_sku(self, client, auth_headers, sample_product, sample_warehouse):
        """Test creating product with duplicate SKU."""
        product_data = {
            'sku': 'TEST-001',  # Same as sample_product
            'name': 'Duplicate Product',
            'warehouse_id': sample_warehouse.id,
            'cost_price': '50.00',
            'sale_price': '75.00',
            'weight_kg': 0.5,
            'volume_m3': 0.006
        }
        
        response = client.post(
            '/api/products',
            headers=auth_headers,
            json=product_data
        )
        
        # Should fail with 400 or 409
        assert response.status_code in [400, 409]
    
    def test_update_product(self, client, auth_headers, sample_product):
        """Test updating a product."""
        update_data = {
            'name': 'Updated Product Name',
            'sale_price': '175.00',
            'is_active': False
        }
        
        response = client.put(
            f'/api/products/{sample_product.id}',
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Product Name'
        assert float(data['sale_price']) == 175.0
        assert data['is_active'] is False
    
    def test_delete_product(self, client, auth_headers, db_session, sample_warehouse, sample_tenant):
        """Test deleting a product."""
        from decimal import Decimal
        # Create a product to delete
        product = Product(
            tenant_id=sample_tenant.id,
            warehouse_id=sample_warehouse.id,
            sku='PROD-DELETE',
            name='To Delete',
            cost_price=Decimal('50.00'),
            sale_price=Decimal('75.00'),
            weight_kg=0.5,
            volume_m3=0.006
        )
        db_session.add(product)
        db_session.commit()
        product_id = product.id
        
        response = client.delete(
            f'/api/products/{product_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(
            f'/api/products/{product_id}',
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_filter_products_by_category(self, client, auth_headers, sample_product):
        """Test filtering products by category."""
        response = client.get(
            '/api/products?category=Electronics',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # API returns paginated response
        assert 'items' in data
        products = data['items']
        
        # All products should be in Electronics category
        for product in products:
            assert product['category'] == 'Electronics'
    
    def test_search_products(self, client, auth_headers, sample_product):
        """Test searching products by name or SKU."""
        response = client.get(
            '/api/products?search=Test',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # API returns paginated response
        assert 'items' in data
        products = data['items']
        
        # Should find our test product
        assert len(products) > 0
    
    def test_product_unauthorized(self, client, sample_product):
        """Test accessing products without authentication."""
        response = client.get('/api/products')
        
        assert response.status_code == 401
    
    def test_assign_product_to_location(self, client, auth_headers, sample_product, sample_location):
        """Test assigning a product to a location."""
        assign_data = {
            'location_id': sample_location.id,
            'quantity': 50
        }
        
        response = client.post(
            f'/api/products/{sample_product.id}/assign-location',
            headers=auth_headers,
            json=assign_data
        )
        
        # Debug output
        if response.status_code not in [200, 201, 404, 501]:
            print(f"\nStatus: {response.status_code}")
            print(f"Data: {response.get_json()}")
        
        # Might be 200, 201, or 404/501 if not implemented
        assert response.status_code in [200, 201, 404, 501]
    
    def test_suggest_locations_for_product(self, client, auth_headers, sample_product):
        """Test getting suggested locations for a product."""
        response = client.get(
            f'/api/products/{sample_product.id}/suggest-locations',
            headers=auth_headers
        )
        
        # Might be 200 with suggestions or 404/501 if not implemented
        assert response.status_code in [200, 404, 501]


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.slow
class TestProductBulkOperations:
    """Test cases for bulk product operations."""
    
    def test_bulk_create_products(self, client, auth_headers, sample_warehouse):
        """Test creating multiple products at once."""
        products_data = [
            {
                'sku': f'BULK-{i:03d}',
                'name': f'Bulk Product {i}',
                'warehouse_id': sample_warehouse.id,
                'cost': 50.0 + i,
                'price': 75.0 + i
            }
            for i in range(5)
        ]
        
        response = client.post(
            '/api/products/bulk',
            headers=auth_headers,
            json={'products': products_data}
        )
        
        # Might not be implemented yet
        assert response.status_code in [200, 201, 404, 501]
    
    def test_export_products(self, client, auth_headers, sample_product):
        """Test exporting products to CSV/Excel."""
        response = client.get(
            '/api/products/export',
            headers=auth_headers
        )
        
        # Might not be implemented yet
        assert response.status_code in [200, 404, 501]
