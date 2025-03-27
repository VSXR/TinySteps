from abc import ABC, abstractmethod
from typing import Optional, Type
from django.db.models import Model, QuerySet, Q


class BaseRepository(ABC):
    """
    Base repository interface following the Repository Pattern.
    This abstract base class defines the standard interface that all repositories should implement.
    """
    
    @property
    @abstractmethod
    def model(self) -> Type[Model]:
        """Return the model class that this repository manages"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Model:
        """
        Get a single entity by ID
        :param id: Primary key of the entity
        :return: The entity object
        :raises: Model.DoesNotExist if no entity with the given ID exists
        """
        pass
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        """
        Get all entities
        :return: QuerySet of all entities
        """
        pass
    
    @abstractmethod
    def filter(self, **criteria) -> QuerySet:
        """
        Filter entities by criteria
        :param criteria: Filtering criteria
        :return: QuerySet of filtered entities
        """
        pass
    
    @abstractmethod
    def create(self, **data) -> Model:
        """
        Create a new entity
        :param data: The data to create the entity with
        :return: The created entity
        """
        pass
    
    @abstractmethod
    def update(self, entity: Model, **data) -> Model:
        """
        Update an existing entity
        :param entity: The entity to update
        :param data: The data to update the entity with
        :return: The updated entity
        """
        pass
    
    @abstractmethod
    def delete(self, entity: Model) -> None:
        """
        Delete an entity
        :param entity: The entity to delete
        """
        pass


class GenericRepository(BaseRepository):
    """
    Generic implementation of the BaseRepository interface.
    This class can be used as a base for concrete repositories.
    """
    
    def __init__(self, model_class: Type[Model]):
        self._model_class = model_class
    
    @property
    def model(self) -> Type[Model]:
        return self._model_class
    
    # Read operations
    def get_by_id(self, id: int) -> Model:
        """Get a single entity by ID"""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(self.model, pk=id)
    
    def get_all(self) -> QuerySet:
        """Get all entities"""
        return self.model.objects.all()
    
    def filter(self, **criteria) -> QuerySet:
        """Filter entities by criteria"""
        return self.model.objects.filter(**criteria)
    
    def get_first(self, **criteria) -> Optional[Model]:
        """Get the first entity matching criteria or None"""
        try:
            return self.model.objects.filter(**criteria).first()
        except self.model.DoesNotExist:
            return None
    
    def count(self) -> int:
        """Count all entities"""
        return self.model.objects.count()
    
    def exists(self, **criteria) -> bool:
        """Check if any entity matches the criteria"""
        return self.model.objects.filter(**criteria).exists()
    
    def get_random(self, count=1):
        """Get random entities"""
        return self.model.objects.order_by('?')[:count]
    
    def get_recent(self, count=5):
        """Get most recent entities"""
        # Try to use created_at if it exists
        if hasattr(self.model, 'created_at'):
            return self.model.objects.order_by('-created_at')[:count]
        # Fall back to primary key
        return self.model.objects.order_by('-pk')[:count]
    
    def search(self, query, fields):
        """
        Search entities by query across multiple fields
        :param query: The search query
        :param fields: List of field names to search in
        :return: QuerySet of matching entities
        """
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        return self.model.objects.filter(q_objects)
    
    # Write operations
    def create(self, **data) -> Model:
        """Create a new entity"""
        entity = self.model(**data)
        entity.save()
        return entity
    
    def update(self, entity: Model, **data) -> Model:
        """Update an existing entity"""
        for key, value in data.items():
            setattr(entity, key, value)
        entity.save()
        return entity
    
    def delete(self, entity: Model) -> None:
        """Delete an entity"""
        entity.delete()
    
    def get_or_create(self, defaults=None, **criteria):
        """Get an entity or create it if it doesn't exist"""
        return self.model.objects.get_or_create(defaults=defaults or {}, **criteria)
    
    def update_or_create(self, defaults=None, **criteria):
        """Update an entity or create it if it doesn't exist"""
        return self.model.objects.update_or_create(defaults=defaults or {}, **criteria)