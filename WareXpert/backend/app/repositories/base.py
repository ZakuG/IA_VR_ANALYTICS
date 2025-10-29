"""Base repository class with common database operations."""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy import func, or_
from sqlalchemy.orm import Query
from app import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository with CRUD operations."""
    
    def __init__(self, model: type[T]):
        """Initialize repository with model class.
        
        Args:
            model: SQLAlchemy model class
        """
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity instance or None
        """
        return db.session.query(self.model).get(id)
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all entities with optional filters.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            List of entities
        """
        query = db.session.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.all()
    
    def get_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> tuple[List[T], int]:
        """Get paginated entities.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            filters: Dictionary of filters to apply
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Tuple of (entities list, total count)
        """
        query = db.session.query(self.model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if hasattr(self.model, sort_by):
            order_column = getattr(self.model, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # Apply pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        return query.all(), total
    
    def create(self, **kwargs) -> T:
        """Create new entity.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            Created entity
        """
        entity = self.model(**kwargs)
        db.session.add(entity)
        db.session.commit()
        return entity
    
    def update(self, entity: T, **kwargs) -> T:
        """Update entity.
        
        Args:
            entity: Entity to update
            **kwargs: Attributes to update
            
        Returns:
            Updated entity
        """
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        db.session.commit()
        return entity
    
    def delete(self, entity: T) -> None:
        """Delete entity.
        
        Args:
            entity: Entity to delete
        """
        db.session.delete(entity)
        db.session.commit()
    
    def exists(self, **kwargs) -> bool:
        """Check if entity exists.
        
        Args:
            **kwargs: Filter conditions
            
        Returns:
            True if entity exists
        """
        query = db.session.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return db.session.query(query.exists()).scalar()
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Count of entities
        """
        query = db.session.query(func.count(self.model.id))
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.scalar()
    
    def search(
        self,
        search_term: str,
        search_fields: List[str],
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[T], int]:
        """Search entities by term.
        
        Args:
            search_term: Search term
            search_fields: Fields to search in
            filters: Additional filters
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (entities list, total count)
        """
        query = db.session.query(self.model)
        
        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                column = getattr(self.model, field)
                search_conditions.append(
                    column.ilike(f'%{search_term}%')
                )
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Apply additional filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.filter(getattr(self.model, key) == value)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        return query.all(), total
