from django.apps import apps
from django.utils.functional import LazyObject

class GuideType_Registry:
    """Registry for guide types implementing OCP"""
    _registry = {}
    
    @classmethod
    def register(cls, guide_type, model_class, service_class, template_prefix):
        """Register a new guide type with its associated classes"""
        cls._registry[guide_type] = {
            'model': model_class,
            'service': service_class,
            'template_prefix': template_prefix,
        }
    
    @classmethod
    def get_model_class(cls, guide_type):
        """Get the model class for a guide type"""
        return cls._registry.get(guide_type, {}).get('model')
    
    @classmethod
    def get_service_class(cls, guide_type):
        """Get the service class for a guide type"""
        return cls._registry.get(guide_type, {}).get('service')
    
    @classmethod
    def get_template_prefix(cls, guide_type):
        """Get the template prefix for a guide type"""
        return cls._registry.get(guide_type, {}).get('template_prefix')
    
    @classmethod
    def get_all_guide_types(cls):
        """Get all registered guide types"""
        return cls._registry.keys()
    
    @classmethod
    def initialize(cls):
        """Initialize the registry with default guide types"""
        # Use lazy loading for models via apps.get_model
        NutritionGuides_Model = apps.get_model('tinySteps', 'NutritionGuides_Model')
        ParentsGuides_Model = apps.get_model('tinySteps', 'ParentsGuides_Model')
        
        # Import service classes here to avoid circular imports
        from .services import NutritionGuide_Service, ParentGuide_Service
        
        # Register guide types with their components
        cls.register('nutrition', NutritionGuides_Model, NutritionGuide_Service, 'guides/nutrition')
        cls.register('parent', ParentsGuides_Model, ParentGuide_Service, 'guides/parents')