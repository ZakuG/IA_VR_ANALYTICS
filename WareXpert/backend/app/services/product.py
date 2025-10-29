"""Product service with business logic."""
from typing import List, Optional, Dict, Any, Tuple
import qrcode
from io import BytesIO
import base64
from marshmallow import ValidationError
from app.repositories.product import (
    ProductRepository,
    StockRepository,
    StockMovementRepository
)
from app.repositories.warehouse import LocationRepository
from app.models.inventory import Product, Stock


class ProductService:
    """Service for product business logic."""
    
    def __init__(self):
        """Initialize product service."""
        self.product_repo = ProductRepository()
        self.stock_repo = StockRepository()
        self.movement_repo = StockMovementRepository()
        self.location_repo = LocationRepository()
    
    def create_product(
        self,
        tenant_id: int,
        data: Dict[str, Any]
    ) -> Product:
        """Create a new product.
        
        Args:
            tenant_id: Tenant ID
            data: Product data
            
        Returns:
            Created product
            
        Raises:
            ValidationError: If SKU already exists
        """
        # Check if SKU already exists for this tenant
        if self.product_repo.get_by_sku(data['sku'], tenant_id):
            raise ValidationError('SKU already exists for this tenant')
        
        # Check barcode uniqueness if provided
        if data.get('barcode'):
            if self.product_repo.get_by_barcode(data['barcode'], tenant_id):
                raise ValidationError('Barcode already exists for this tenant')
        
        # Create product
        product = self.product_repo.create(
            tenant_id=tenant_id,
            **data
        )
        
        # Generate QR code
        self._generate_qr_code(product)
        
        return product
    
    def get_product(self, product_id: int, tenant_id: int) -> Optional[Product]:
        """Get product by ID.
        
        Args:
            product_id: Product ID
            tenant_id: Tenant ID
            
        Returns:
            Product or None (also returns None if soft-deleted)
        """
        product = self.product_repo.get_by_id(product_id)
        
        # Verify tenant ownership and active status
        if product and (product.tenant_id != tenant_id or not product.is_active):
            return None
        
        return product
    
    def search_products(
        self,
        tenant_id: int,
        **kwargs
    ) -> Tuple[List[Product], int]:
        """Search products with filters.
        
        Args:
            tenant_id: Tenant ID
            **kwargs: Search parameters (maps 'search' to 'search_term')
            
        Returns:
            Tuple of (products list, total count)
        """
        # Map 'search' to 'search_term' for repository compatibility
        if 'search' in kwargs:
            kwargs['search_term'] = kwargs.pop('search')
        
        return self.product_repo.search_products(
            tenant_id=tenant_id,
            **kwargs
        )
    
    def update_product(
        self,
        product_id: int,
        tenant_id: int,
        data: Dict[str, Any]
    ) -> Optional[Product]:
        """Update product.
        
        Args:
            product_id: Product ID
            tenant_id: Tenant ID
            data: Update data
            
        Returns:
            Updated product or None
            
        Raises:
            ValidationError: If SKU/barcode already exists
        """
        product = self.get_product(product_id, tenant_id)
        if not product:
            return None
        
        # Check SKU uniqueness if changing SKU
        if 'sku' in data and data['sku'] != product.sku:
            existing = self.product_repo.get_by_sku(data['sku'], tenant_id)
            if existing:
                raise ValidationError('SKU already exists for this tenant')
        
        # Check barcode uniqueness if changing barcode
        if 'barcode' in data and data['barcode'] and data['barcode'] != product.barcode:
            existing = self.product_repo.get_by_barcode(data['barcode'], tenant_id)
            if existing:
                raise ValidationError('Barcode already exists for this tenant')
        
        # Update product
        updated_product = self.product_repo.update(product, **data)
        
        # Regenerate QR if SKU changed
        if 'sku' in data and data['sku'] != product.sku:
            self._generate_qr_code(updated_product)
        
        return updated_product
    
    def delete_product(self, product_id: int, tenant_id: int) -> bool:
        """Delete product (soft delete).
        
        Args:
            product_id: Product ID
            tenant_id: Tenant ID
            
        Returns:
            True if deleted successfully
        """
        product = self.get_product(product_id, tenant_id)
        if not product:
            return False
        
        # Check if product has stock
        total_stock = self.stock_repo.get_total_stock(product_id)
        if total_stock > 0:
            raise ValidationError('Cannot delete product with stock')
        
        # Soft delete
        self.product_repo.update(product, is_active=False)
        return True
    
    def assign_to_location(
        self,
        product_id: int,
        tenant_id: int,
        location_id: int,
        quantity: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Assign product to a location.
        
        Args:
            product_id: Product ID
            tenant_id: Tenant ID
            location_id: Location ID
            quantity: Quantity to assign
            user_id: User performing the operation
            
        Returns:
            Assignment result
            
        Raises:
            ValidationError: If product/location not found or insufficient capacity
        """
        # Verify product
        product = self.get_product(product_id, tenant_id)
        if not product:
            raise ValidationError('Product not found')
        
        # Verify location
        location = self.location_repo.get_by_id(location_id)
        if not location or not location.is_active:
            raise ValidationError('Location not found or inactive')
        
        # Check capacity
        required_volume = product.volume_m3 * quantity
        required_weight = product.weight_kg * quantity
        
        available_m3 = location.capacity_m3 - location.used_m3
        available_kg = location.capacity_kg - location.used_kg
        available_items = (location.max_stackable or float('inf')) - location.current_items
        
        if required_volume > available_m3:
            raise ValidationError(f'Insufficient volume capacity. Available: {available_m3:.2f}m³, Required: {required_volume:.2f}m³')
        
        if required_weight > available_kg:
            raise ValidationError(f'Insufficient weight capacity. Available: {available_kg:.2f}kg, Required: {required_weight:.2f}kg')
        
        if location.max_stackable and quantity > available_items:
            raise ValidationError(f'Insufficient item capacity. Available: {available_items}, Required: {quantity}')
        
        # Add stock
        stock = self.stock_repo.add_stock(product_id, location_id, quantity)
        
        # Update location capacity
        self.location_repo.update_capacity(
            location_id=location_id,
            volume_delta=required_volume,
            weight_delta=required_weight,
            items_delta=quantity
        )
        
        # Record movement
        self.movement_repo.record_movement(
            product_id=product_id,
            movement_type='IN',
            quantity=quantity,
            location_to_id=location_id,
            user_id=user_id,
            reason='Product assigned to location'
        )
        
        return {
            'success': True,
            'stock': stock.to_dict(),
            'location': location.to_dict(),
            'message': f'Successfully assigned {quantity} units to {location.code}'
        }
    
    def suggest_locations(
        self,
        product_id: int,
        tenant_id: int,
        quantity: int = 1,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Suggest best locations for a product.
        
        Args:
            product_id: Product ID
            tenant_id: Tenant ID
            quantity: Quantity to place
            limit: Maximum suggestions
            
        Returns:
            List of location suggestions with scores
        """
        product = self.get_product(product_id, tenant_id)
        if not product:
            return []
        
        required_volume = product.volume_m3 * quantity
        required_weight = product.weight_kg * quantity
        
        # Get available locations
        locations = self.location_repo.get_available_locations(
            warehouse_id=product.warehouse_id,
            required_volume=required_volume,
            required_weight=required_weight
        )
        
        suggestions = []
        for location in locations[:limit]:
            # Calculate score based on various factors
            score = self._calculate_location_score(product, location, quantity)
            
            reasons = []
            
            # Zone preference
            if product.total_sales > 100:  # High rotation
                if location.zone == 'PICKING':
                    reasons.append('Picking zone optimal for high-rotation items')
            else:
                if location.zone == 'STORAGE':
                    reasons.append('Storage zone suitable for low-rotation items')
            
            # Capacity efficiency
            capacity_usage = (required_volume / location.capacity_m3) * 100
            if capacity_usage < 80:
                reasons.append(f'Good capacity fit ({capacity_usage:.1f}% of location)')
            
            # Priority level
            if location.priority_level >= 7:
                reasons.append('High-priority location')
            
            suggestions.append({
                'location_id': location.id,
                'location_code': location.code,
                'zone': location.zone,
                'score': round(score, 2),
                'reasons': reasons,
                'available_capacity_m3': location.capacity_m3 - location.used_m3,
                'available_capacity_kg': location.max_capacity_kg - location.current_capacity_kg,
            })
        
        # Sort by score descending
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return suggestions
    
    def get_product_stock_summary(
        self,
        product_id: int,
        tenant_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get stock summary for a product.
        
        Args:
            product_id: Product ID
            tenant_id: Tenant ID
            
        Returns:
            Stock summary or None
        """
        product = self.get_product(product_id, tenant_id)
        if not product:
            return None
        
        stock_records = self.stock_repo.get_product_stock(product_id)
        
        total_quantity = sum(s.quantity for s in stock_records)
        total_reserved = sum(s.reserved for s in stock_records)
        total_available = total_quantity - total_reserved
        
        locations = []
        for stock in stock_records:
            location = self.location_repo.get_by_id(stock.location_id)
            if location:
                locations.append({
                    'location_id': location.id,
                    'location_code': location.code,
                    'zone': location.zone,
                    'quantity': stock.quantity,
                    'reserved': stock.reserved,
                    'available': stock.available,
                })
        
        return {
            'product_id': product_id,
            'sku': product.sku,
            'name': product.name,
            'total_quantity': total_quantity,
            'total_reserved': total_reserved,
            'total_available': total_available,
            'stock_min': product.stock_min,
            'reorder_point': product.reorder_point,
            'needs_reorder': total_available <= product.reorder_point,
            'locations': locations,
        }
    
    def _generate_qr_code(self, product: Product) -> None:
        """Generate QR code for product.
        
        Args:
            product: Product instance
        """
        # Generate QR code data (could be URL, SKU, or structured data)
        qr_data = f"PRODUCT:{product.id}:{product.sku}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 (for simple storage, in production use S3)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Update product
        product.qr_code = f"data:image/png;base64,{qr_code_base64}"
        self.product_repo.update(product, qr_code=product.qr_code)
    
    def _calculate_location_score(
        self,
        product: Product,
        location,
        quantity: int
    ) -> float:
        """Calculate location suitability score.
        
        Args:
            product: Product instance
            location: Location instance
            quantity: Quantity to place
            
        Returns:
            Score (0-100)
        """
        score = 0.0
        
        # Zone score (40 points max)
        if product.total_sales > 100:  # High rotation
            if location.zone == 'PICKING':
                score += 40
            elif location.zone == 'STORAGE':
                score += 20
        else:  # Low rotation
            if location.zone == 'STORAGE':
                score += 40
            elif location.zone == 'PICKING':
                score += 15
        
        # Capacity efficiency score (30 points max)
        required_volume = product.volume_m3 * quantity
        capacity_usage = (required_volume / location.capacity_m3) * 100
        
        if 50 <= capacity_usage <= 80:  # Optimal range
            score += 30
        elif 30 <= capacity_usage < 50:
            score += 20
        elif 80 < capacity_usage <= 90:
            score += 15
        else:
            score += 5
        
        # Priority level score (20 points max)
        score += (location.priority_level / 10) * 20
        
        # Proximity score (10 points max) - simplified
        # In production, calculate actual distance
        if location.position_x < 10 and location.position_y < 10:  # Close to entrance
            score += 10
        else:
            score += 5
        
        return min(100.0, score)
