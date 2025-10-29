"""Product repository for database operations."""
from typing import List, Optional, Tuple
from sqlalchemy import or_, and_, func
from app.repositories.base import BaseRepository
from app.models.inventory import Product, Stock, StockMovement
from app import db


class ProductRepository(BaseRepository[Product]):
    """Repository for product operations."""
    
    def __init__(self):
        """Initialize product repository."""
        super().__init__(Product)
    
    def get_by_sku(self, sku: str, tenant_id: int) -> Optional[Product]:
        """Get product by SKU and tenant.
        
        Args:
            sku: Product SKU
            tenant_id: Tenant ID
            
        Returns:
            Product instance or None
        """
        return db.session.query(Product).filter_by(
            sku=sku,
            tenant_id=tenant_id
        ).first()
    
    def get_by_barcode(self, barcode: str, tenant_id: int) -> Optional[Product]:
        """Get product by barcode and tenant.
        
        Args:
            barcode: Product barcode
            tenant_id: Tenant ID
            
        Returns:
            Product instance or None
        """
        return db.session.query(Product).filter_by(
            barcode=barcode,
            tenant_id=tenant_id
        ).first()
    
    def search_products(
        self,
        tenant_id: int,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        warehouse_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        low_stock: bool = False,
        out_of_stock: bool = False,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[Product], int]:
        """Advanced product search.
        
        Args:
            tenant_id: Tenant ID
            search_term: Search in name, SKU, description
            category: Filter by category
            brand: Filter by brand
            warehouse_id: Filter by warehouse
            is_active: Filter by active status
            min_price: Minimum price
            max_price: Maximum price
            low_stock: Show only low stock items
            out_of_stock: Show only out of stock items
            page: Page number
            per_page: Items per page
            sort_by: Sort field
            sort_order: Sort order
            
        Returns:
            Tuple of (products list, total count)
        """
        query = db.session.query(Product).filter_by(tenant_id=tenant_id)
        
        # Search term
        if search_term:
            search_filter = or_(
                Product.name.ilike(f'%{search_term}%'),
                Product.sku.ilike(f'%{search_term}%'),
                Product.description.ilike(f'%{search_term}%'),
                Product.barcode.ilike(f'%{search_term}%')
            )
            query = query.filter(search_filter)
        
        # Filters
        if category:
            query = query.filter_by(category=category)
        
        if brand:
            query = query.filter_by(brand=brand)
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        if min_price is not None:
            query = query.filter(Product.sale_price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.sale_price <= max_price)
        
        # Stock filters (would need to calculate total stock)
        # For now, simplified version
        
        # Get total count
        total = query.count()
        
        # Sorting
        if hasattr(Product, sort_by):
            order_column = getattr(Product, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # Pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        return query.all(), total
    
    def get_low_stock_products(
        self,
        tenant_id: int,
        warehouse_id: Optional[int] = None
    ) -> List[Product]:
        """Get products with stock below reorder point.
        
        Args:
            tenant_id: Tenant ID
            warehouse_id: Optional warehouse filter
            
        Returns:
            List of low stock products
        """
        # This would need to calculate total stock from Stock table
        # Simplified version for now
        query = db.session.query(Product).filter_by(
            tenant_id=tenant_id,
            is_active=True
        )
        
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        
        # Would need JOIN with Stock table for accurate count
        return query.all()
    
    def get_categories(self, tenant_id: int) -> List[str]:
        """Get all product categories for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of category names
        """
        categories = db.session.query(Product.category).filter(
            Product.tenant_id == tenant_id,
            Product.category.isnot(None)
        ).distinct().all()
        
        return [cat[0] for cat in categories if cat[0]]
    
    def get_brands(self, tenant_id: int) -> List[str]:
        """Get all product brands for tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of brand names
        """
        brands = db.session.query(Product.brand).filter(
            Product.tenant_id == tenant_id,
            Product.brand.isnot(None)
        ).distinct().all()
        
        return [brand[0] for brand in brands if brand[0]]


class StockRepository(BaseRepository[Stock]):
    """Repository for stock operations."""
    
    def __init__(self):
        """Initialize stock repository."""
        super().__init__(Stock)
    
    def get_by_product_and_location(
        self,
        product_id: int,
        location_id: int
    ) -> Optional[Stock]:
        """Get stock for product at specific location.
        
        Args:
            product_id: Product ID
            location_id: Location ID
            
        Returns:
            Stock instance or None
        """
        return db.session.query(Stock).filter_by(
            product_id=product_id,
            location_id=location_id
        ).first()
    
    def get_product_stock(self, product_id: int) -> List[Stock]:
        """Get all stock records for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            List of stock records
        """
        return db.session.query(Stock).filter_by(
            product_id=product_id
        ).all()
    
    def get_location_stock(self, location_id: int) -> List[Stock]:
        """Get all stock in a location.
        
        Args:
            location_id: Location ID
            
        Returns:
            List of stock records
        """
        return db.session.query(Stock).filter_by(
            location_id=location_id
        ).all()
    
    def get_total_stock(self, product_id: int) -> int:
        """Get total stock quantity for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Total quantity
        """
        result = db.session.query(func.sum(Stock.quantity)).filter_by(
            product_id=product_id
        ).scalar()
        
        return result or 0
    
    def get_available_stock(self, product_id: int) -> int:
        """Get available (non-reserved) stock for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Available quantity
        """
        result = db.session.query(
            func.sum(Stock.quantity - Stock.reserved)
        ).filter_by(product_id=product_id).scalar()
        
        return result or 0
    
    def add_stock(
        self,
        product_id: int,
        location_id: int,
        quantity: int
    ) -> Stock:
        """Add stock to a location.
        
        Args:
            product_id: Product ID
            location_id: Location ID
            quantity: Quantity to add
            
        Returns:
            Updated or created stock record
        """
        stock = self.get_by_product_and_location(product_id, location_id)
        
        if stock:
            stock.quantity += quantity
        else:
            stock = Stock(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity,
                reserved=0
            )
            db.session.add(stock)
        
        db.session.commit()
        return stock
    
    def remove_stock(
        self,
        product_id: int,
        location_id: int,
        quantity: int
    ) -> Optional[Stock]:
        """Remove stock from a location.
        
        Args:
            product_id: Product ID
            location_id: Location ID
            quantity: Quantity to remove
            
        Returns:
            Updated stock record or None
        """
        stock = self.get_by_product_and_location(product_id, location_id)
        
        if not stock or stock.quantity < quantity:
            return None
        
        stock.quantity -= quantity
        db.session.commit()
        
        return stock
    
    def reserve_stock(
        self,
        product_id: int,
        location_id: int,
        quantity: int
    ) -> bool:
        """Reserve stock for an order.
        
        Args:
            product_id: Product ID
            location_id: Location ID
            quantity: Quantity to reserve
            
        Returns:
            True if reservation successful
        """
        stock = self.get_by_product_and_location(product_id, location_id)
        
        if not stock or (stock.quantity - stock.reserved) < quantity:
            return False
        
        stock.reserved += quantity
        db.session.commit()
        
        return True
    
    def release_reservation(
        self,
        product_id: int,
        location_id: int,
        quantity: int
    ) -> bool:
        """Release reserved stock.
        
        Args:
            product_id: Product ID
            location_id: Location ID
            quantity: Quantity to release
            
        Returns:
            True if release successful
        """
        stock = self.get_by_product_and_location(product_id, location_id)
        
        if not stock or stock.reserved < quantity:
            return False
        
        stock.reserved -= quantity
        db.session.commit()
        
        return True


class StockMovementRepository(BaseRepository[StockMovement]):
    """Repository for stock movement operations."""
    
    def __init__(self):
        """Initialize stock movement repository."""
        super().__init__(StockMovement)
    
    def get_product_movements(
        self,
        product_id: int,
        limit: int = 50
    ) -> List[StockMovement]:
        """Get recent movements for a product.
        
        Args:
            product_id: Product ID
            limit: Maximum number of records
            
        Returns:
            List of movements
        """
        return db.session.query(StockMovement).filter_by(
            product_id=product_id
        ).order_by(StockMovement.created_at.desc()).limit(limit).all()
    
    def record_movement(
        self,
        product_id: int,
        movement_type: str,
        quantity: int,
        location_from_id: Optional[int] = None,
        location_to_id: Optional[int] = None,
        user_id: Optional[int] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> StockMovement:
        """Record a stock movement.
        
        Args:
            product_id: Product ID
            movement_type: Type of movement (IN, OUT, TRANSFER, etc.)
            quantity: Quantity moved
            location_from_id: Source location
            location_to_id: Destination location
            user_id: User who performed the movement
            reference_type: Type of reference document
            reference_id: ID of reference document
            reason: Reason for movement
            
        Returns:
            Created movement record
        """
        movement = StockMovement(
            product_id=product_id,
            type=movement_type,
            quantity=quantity,
            location_from_id=location_from_id,
            location_to_id=location_to_id,
            user_id=user_id,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason
        )
        
        db.session.add(movement)
        db.session.commit()
        
        return movement
