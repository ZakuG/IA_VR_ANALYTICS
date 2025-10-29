"""Warehouse service with business logic."""
from typing import List, Optional, Dict, Any, Tuple
from marshmallow import ValidationError
from app.repositories.warehouse import WarehouseRepository, LocationRepository
from app.models.warehouse import Warehouse, Location
from app import db


class WarehouseService:
    """Service for warehouse business logic."""
    
    def __init__(self):
        """Initialize warehouse service."""
        self.warehouse_repo = WarehouseRepository()
        self.location_repo = LocationRepository()
    
    def create_warehouse(
        self,
        tenant_id: int,
        data: Dict[str, Any]
    ) -> Warehouse:
        """Create a new warehouse.
        
        Args:
            tenant_id: Tenant ID
            data: Warehouse data
            
        Returns:
            Created warehouse
            
        Raises:
            ValidationError: If warehouse code already exists
        """
        # Check if code already exists for this tenant
        if self.warehouse_repo.get_by_code(data['code'], tenant_id):
            raise ValidationError('Warehouse code already exists for this tenant')
        
        # Create warehouse
        warehouse = self.warehouse_repo.create(
            tenant_id=tenant_id,
            **data
        )
        
        return warehouse
    
    def get_warehouse(self, warehouse_id: int, tenant_id: int) -> Optional[Warehouse]:
        """Get warehouse by ID.
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            
        Returns:
            Warehouse or None (also returns None if soft-deleted)
        """
        warehouse = self.warehouse_repo.get_by_id(warehouse_id)
        
        # Verify tenant ownership and active status
        if warehouse and (warehouse.tenant_id != tenant_id or not warehouse.is_active):
            return None
        
        return warehouse
    
    def list_warehouses(
        self,
        tenant_id: int,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[Warehouse], int]:
        """List warehouses with pagination.
        
        Args:
            tenant_id: Tenant ID
            page: Page number
            per_page: Items per page
            filters: Additional filters
            sort_by: Sort field
            sort_order: Sort order
            
        Returns:
            Tuple of (warehouses list, total count)
        """
        # Add tenant filter
        if filters is None:
            filters = {}
        filters['tenant_id'] = tenant_id
        
        return self.warehouse_repo.get_paginated(
            page=page,
            per_page=per_page,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order
        )
    
    def update_warehouse(
        self,
        warehouse_id: int,
        tenant_id: int,
        data: Dict[str, Any]
    ) -> Optional[Warehouse]:
        """Update warehouse.
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            data: Update data
            
        Returns:
            Updated warehouse or None
            
        Raises:
            ValidationError: If code already exists
        """
        warehouse = self.get_warehouse(warehouse_id, tenant_id)
        if not warehouse:
            return None
        
        # Check code uniqueness if changing code
        if 'code' in data and data['code'] != warehouse.code:
            existing = self.warehouse_repo.get_by_code(data['code'], tenant_id)
            if existing:
                raise ValidationError('Warehouse code already exists for this tenant')
        
        return self.warehouse_repo.update(warehouse, **data)
    
    def delete_warehouse(self, warehouse_id: int, tenant_id: int) -> bool:
        """Delete warehouse (soft delete by setting is_active=False).
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            
        Returns:
            True if deleted successfully
        """
        warehouse = self.get_warehouse(warehouse_id, tenant_id)
        if not warehouse:
            return False
        
        # Soft delete
        self.warehouse_repo.update(warehouse, is_active=False)
        return True
    
    def get_warehouse_stats(self, warehouse_id: int, tenant_id: int) -> Optional[Dict[str, Any]]:
        """Get warehouse statistics.
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            
        Returns:
            Statistics dictionary or None
        """
        warehouse = self.get_warehouse(warehouse_id, tenant_id)
        if not warehouse:
            return None
        
        locations = self.location_repo.get_by_warehouse(warehouse_id, is_active=True)
        
        return {
            'total_locations': len(locations),
            'active_locations': sum(1 for loc in locations if loc.is_active),
            'capacity_usage_percent': warehouse.capacity_usage_percent,
            'available_capacity_m3': warehouse.available_capacity_m3,
            'used_capacity_m3': warehouse.used_capacity_m3,
            'total_capacity_m3': warehouse.total_capacity_m3,
        }


class LocationService:
    """Service for location business logic."""
    
    def __init__(self):
        """Initialize location service."""
        self.location_repo = LocationRepository()
        self.warehouse_repo = WarehouseRepository()
    
    def create_location(
        self,
        warehouse_id: int,
        tenant_id: int,
        data: Dict[str, Any]
    ) -> Location:
        """Create a new location.
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            data: Location data
            
        Returns:
            Created location
            
        Raises:
            ValidationError: If location code exists or warehouse not found
        """
        # Verify warehouse exists and belongs to tenant
        warehouse = self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            raise ValidationError('Warehouse not found')
        
        # Check if code already exists for this warehouse
        if self.location_repo.get_by_code(data['code'], warehouse_id):
            raise ValidationError('Location code already exists for this warehouse')
        
        # Create location
        location = self.location_repo.create(
            warehouse_id=warehouse_id,
            **data
        )
        
        return location
    
    def get_location(
        self,
        location_id: int,
        tenant_id: Optional[int] = None
    ) -> Optional[Location]:
        """Get location by ID.
        
        Args:
            location_id: Location ID
            tenant_id: Optional tenant ID for verification
            
        Returns:
            Location or None
        """
        location = self.location_repo.get_by_id(location_id)
        
        # Verify tenant ownership if provided
        if location and tenant_id:
            warehouse = self.warehouse_repo.get_by_id(location.warehouse_id)
            if warehouse.tenant_id != tenant_id:
                return None
        
        return location
    
    def list_locations(
        self,
        warehouse_id: int,
        tenant_id: int,
        is_active: Optional[bool] = None,
        zone: Optional[str] = None
    ) -> List[Location]:
        """List locations for a warehouse.
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            is_active: Filter by active status
            zone: Filter by zone
            
        Returns:
            List of locations
        """
        # Verify warehouse belongs to tenant
        warehouse = self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            return []
        
        return self.location_repo.get_by_warehouse(
            warehouse_id=warehouse_id,
            is_active=is_active,
            zone=zone
        )
    
    def update_location(
        self,
        location_id: int,
        tenant_id: int,
        data: Dict[str, Any]
    ) -> Optional[Location]:
        """Update location.
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            data: Update data
            
        Returns:
            Updated location or None
            
        Raises:
            ValidationError: If code already exists
        """
        location = self.get_location(location_id, tenant_id)
        if not location:
            return None
        
        # Check code uniqueness if changing code
        if 'code' in data and data['code'] != location.code:
            existing = self.location_repo.get_by_code(data['code'], location.warehouse_id)
            if existing:
                raise ValidationError('Location code already exists for this warehouse')
        
        return self.location_repo.update(location, **data)
    
    def delete_location(self, location_id: int, tenant_id: int) -> bool:
        """Delete location (soft delete).
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            
        Returns:
            True if deleted successfully
        """
        location = self.get_location(location_id, tenant_id)
        if not location:
            return False
        
        # Check if location has stock
        if location.current_items > 0:
            raise ValidationError('Cannot delete location with stock')
        
        # Soft delete
        self.location_repo.update(location, is_active=False)
        return True
    
    def find_available_locations(
        self,
        warehouse_id: int,
        tenant_id: int,
        required_volume: float,
        required_weight: float,
        zone: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find available locations for a product.
        
        Args:
            warehouse_id: Warehouse ID
            tenant_id: Tenant ID
            required_volume: Required volume in m3
            required_weight: Required weight in kg
            zone: Preferred zone
            limit: Maximum results
            
        Returns:
            List of location dictionaries with availability info
        """
        # Verify warehouse
        warehouse = self.warehouse_repo.get_by_id(warehouse_id)
        if not warehouse or warehouse.tenant_id != tenant_id:
            return []
        
        locations = self.location_repo.get_available_locations(
            warehouse_id=warehouse_id,
            required_volume=required_volume,
            required_weight=required_weight,
            zone=zone
        )[:limit]
        
        result = []
        for location in locations:
            available_m3 = location.capacity_m3 - location.used_m3
            available_kg = location.max_capacity_kg - location.current_capacity_kg
            
            result.append({
                'location_id': location.id,
                'code': location.code,
                'zone': location.zone,
                'type': location.type,
                'priority_level': location.priority_level,
                'available_capacity_m3': available_m3,
                'available_capacity_kg': available_kg,
                'capacity_usage_percent': location.current_capacity_usage,
                'is_full': location.is_full,
            })
        
        return result
