"""Warehouse repository for database operations."""
from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.warehouse import Warehouse, Location
from app import db


class WarehouseRepository(BaseRepository[Warehouse]):
    """Repository for warehouse operations."""
    
    def __init__(self):
        """Initialize warehouse repository."""
        super().__init__(Warehouse)
    
    def get_by_code(self, code: str, tenant_id: int) -> Optional[Warehouse]:
        """Get warehouse by code and tenant.
        
        Args:
            code: Warehouse code
            tenant_id: Tenant ID
            
        Returns:
            Warehouse instance or None
        """
        return db.session.query(Warehouse).filter_by(
            code=code,
            tenant_id=tenant_id
        ).first()
    
    def get_by_tenant(
        self,
        tenant_id: int,
        is_active: Optional[bool] = None
    ) -> List[Warehouse]:
        """Get all warehouses for a tenant.
        
        Args:
            tenant_id: Tenant ID
            is_active: Filter by active status
            
        Returns:
            List of warehouses
        """
        query = db.session.query(Warehouse).filter_by(tenant_id=tenant_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.all()
    
    def get_with_locations(self, warehouse_id: int) -> Optional[Warehouse]:
        """Get warehouse with all locations.
        
        Args:
            warehouse_id: Warehouse ID
            
        Returns:
            Warehouse with locations loaded
        """
        return db.session.query(Warehouse).filter_by(
            id=warehouse_id
        ).first()
    
    def update_capacity_usage(self, warehouse_id: int) -> None:
        """Update warehouse capacity usage from locations.
        
        Args:
            warehouse_id: Warehouse ID
        """
        warehouse = self.get_by_id(warehouse_id)
        if not warehouse:
            return
        
        # Calculate total used capacity from all locations
        total_m3 = 0.0
        total_kg = 0.0
        total_items = 0
        
        for location in warehouse.locations:
            total_m3 += location.used_m3
            total_kg += location.current_capacity_kg
            total_items += location.current_items
        
        warehouse.used_capacity_m3 = total_m3
        warehouse.used_capacity_kg = total_kg
        warehouse.used_capacity_items = total_items
        
        db.session.commit()


class LocationRepository(BaseRepository[Location]):
    """Repository for location operations."""
    
    def __init__(self):
        """Initialize location repository."""
        super().__init__(Location)
    
    def get_by_code(self, code: str, warehouse_id: int) -> Optional[Location]:
        """Get location by code and warehouse.
        
        Args:
            code: Location code
            warehouse_id: Warehouse ID
            
        Returns:
            Location instance or None
        """
        return db.session.query(Location).filter_by(
            code=code,
            warehouse_id=warehouse_id
        ).first()
    
    def get_by_warehouse(
        self,
        warehouse_id: int,
        is_active: Optional[bool] = None,
        zone: Optional[str] = None
    ) -> List[Location]:
        """Get all locations for a warehouse.
        
        Args:
            warehouse_id: Warehouse ID
            is_active: Filter by active status
            zone: Filter by zone
            
        Returns:
            List of locations
        """
        query = db.session.query(Location).filter_by(warehouse_id=warehouse_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if zone:
            query = query.filter_by(zone=zone)
        
        return query.all()
    
    def get_available_locations(
        self,
        warehouse_id: int,
        required_volume: float,
        required_weight: float,
        zone: Optional[str] = None
    ) -> List[Location]:
        """Get locations with available capacity.
        
        Args:
            warehouse_id: Warehouse ID
            required_volume: Required volume in m3
            required_weight: Required weight in kg
            zone: Filter by zone
            
        Returns:
            List of available locations
        """
        query = db.session.query(Location).filter(
            Location.warehouse_id == warehouse_id,
            Location.is_active == True,
            Location.capacity_m3 - Location.used_m3 >= required_volume,
            Location.capacity_kg - Location.used_kg >= required_weight
        )
        
        # Only filter by max_stackable if it's set (some locations have no limit)
        query = query.filter(
            (Location.max_stackable == None) | (Location.max_stackable > Location.current_items)
        )
        
        if zone:
            query = query.filter_by(zone=zone)
        
        # Order by priority level (higher first), then by available space
        query = query.order_by(
            Location.priority_level.desc(),
            (Location.capacity_m3 - Location.used_m3).asc()
        )
        
        return query.all()
    
    def update_capacity(
        self,
        location_id: int,
        volume_delta: float = 0,
        weight_delta: float = 0,
        items_delta: int = 0
    ) -> None:
        """Update location capacity usage.
        
        Args:
            location_id: Location ID
            volume_delta: Change in volume (can be negative)
            weight_delta: Change in weight (can be negative)
            items_delta: Change in items count (can be negative)
        """
        location = self.get_by_id(location_id)
        if not location:
            return
        
        location.used_m3 += volume_delta
        location.used_kg += weight_delta
        location.current_items += items_delta
        
        # Ensure values don't go negative
        location.used_m3 = max(0, location.used_m3)
        location.used_kg = max(0, location.used_kg)
        location.current_items = max(0, location.current_items)
        
        db.session.commit()
