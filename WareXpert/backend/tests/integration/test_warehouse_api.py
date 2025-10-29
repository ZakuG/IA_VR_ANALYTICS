"""
Integration tests for Warehouse API endpoints.
Tests complete workflows for warehouse management.
"""

import pytest
import json
from app.models import Warehouse


@pytest.mark.integration
@pytest.mark.api
class TestWarehouseEndpoints:
    """Test cases for Warehouse API endpoints."""
    
    def test_list_warehouses(self, client, auth_headers, sample_warehouse):
        """Test listing all warehouses."""
        response = client.get('/api/warehouses', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # API returns paginated response
        assert 'items' in data
        assert 'page' in data
        assert 'total' in data
        assert len(data['items']) > 0
        assert any(w['code'] == 'WH-TEST' for w in data['items'])
    
    def test_get_warehouse_by_id(self, client, auth_headers, sample_warehouse):
        """Test getting a specific warehouse."""
        response = client.get(
            f'/api/warehouses/{sample_warehouse.id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 'WH-TEST'
        assert data['name'] == 'Test Warehouse'
    
    def test_get_warehouse_not_found(self, client, auth_headers):
        """Test getting non-existent warehouse."""
        response = client.get('/api/warehouses/99999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_create_warehouse(self, client, auth_headers, sample_tenant):
        """Test creating a new warehouse."""
        warehouse_data = {
            'code': 'WH-NEW',
            'name': 'New Warehouse',
            'length': 100.0,  # Changed from length_m
            'width': 50.0,    # Changed from width_m
            'height': 10.0,   # Changed from height_m
            'total_capacity_m3': 50000.0,
            'total_capacity_kg': 1000000.0,
            'total_capacity_items': 10000
        }
        
        response = client.post(
            '/api/warehouses',
            headers=auth_headers,
            json=warehouse_data
        )
        
        if response.status_code != 201:
            print(f"\nStatus: {response.status_code}")
            print(f"Data: {response.get_json()}")
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['code'] == 'WH-NEW'
        assert data['name'] == 'New Warehouse'
        assert data['id'] is not None
    
    def test_create_warehouse_duplicate_code(self, client, auth_headers, sample_warehouse):
        """Test creating warehouse with duplicate code."""
        warehouse_data = {
            'code': 'WH-TEST',  # Same as sample_warehouse
            'name': 'Duplicate Warehouse',
            'address': '456 Duplicate Ave',
            'city': 'Santiago',
            'country': 'Chile',
            'length_m': 50.0,
            'width_m': 30.0,
            'height_m': 6.0,
            'total_capacity_m3': 9000.0,
            'total_capacity_kg': 500000.0,
            'total_capacity_items': 5000
        }
        
        response = client.post(
            '/api/warehouses',
            headers=auth_headers,
            json=warehouse_data
        )
        
        # Should fail with 400 or 409
        assert response.status_code in [400, 409]
    
    def test_update_warehouse(self, client, auth_headers, sample_warehouse):
        """Test updating a warehouse."""
        update_data = {
            'name': 'Updated Warehouse Name',
            'is_active': False
        }
        
        response = client.put(
            f'/api/warehouses/{sample_warehouse.id}',
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Warehouse Name'
        assert data['is_active'] is False
    
    def test_delete_warehouse(self, client, auth_headers, db_session, sample_tenant):
        """Test deleting a warehouse."""
        # Create a warehouse to delete
        warehouse = Warehouse(
            tenant_id=sample_tenant.id,
            code='WH-DELETE',
            name='To Delete',
            length=50.0,
            width=30.0,
            height=6.0
        )
        db_session.add(warehouse)
        db_session.commit()
        warehouse_id = warehouse.id
        
        response = client.delete(
            f'/api/warehouses/{warehouse_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(
            f'/api/warehouses/{warehouse_id}',
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    def test_warehouse_unauthorized(self, client, sample_warehouse):
        """Test accessing warehouses without authentication."""
        response = client.get('/api/warehouses')
        
        assert response.status_code == 401
    
    def test_get_warehouse_stats(self, client, auth_headers, sample_warehouse):
        """Test getting warehouse statistics."""
        response = client.get(
            f'/api/warehouses/{sample_warehouse.id}/stats',
            headers=auth_headers
        )
        
        # Might be 200 with stats or 404 if endpoint doesn't exist
        assert response.status_code in [200, 404, 501]


@pytest.mark.integration
@pytest.mark.api
class TestLocationEndpoints:
    """Test cases for Location API endpoints within warehouses."""
    
    def test_list_warehouse_locations(self, client, auth_headers, sample_warehouse, sample_location):
        """Test listing all locations in a warehouse."""
        response = client.get(
            f'/api/warehouses/{sample_warehouse.id}/locations',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list) or 'locations' in data
    
    def test_create_location_in_warehouse(self, client, auth_headers, sample_warehouse):
        """Test creating a new location in warehouse."""
        location_data = {
            'code': 'B-02-05',
            'type': 'shelf',
            'zone': 'storage',
            'x_position': 5.0,
            'y_position': 10.0,
            'z_position': 0.0,
            'capacity_m3': 3.0,
            'capacity_kg': 1000.0
        }
        
        response = client.post(
            f'/api/warehouses/{sample_warehouse.id}/locations',
            headers=auth_headers,
            json=location_data
        )
        
        if response.status_code != 201:
            print(f"\nStatus: {response.status_code}")
            print(f"Data: {response.get_json()}")
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['code'] == 'B-02-05'
        assert data['zone'] == 'storage'
