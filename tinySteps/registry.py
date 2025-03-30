from django.apps import apps

class GuideType_Registry:
    """Registry for guide types"""
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
        """Initialize the registry with default guide types
        
        WARNING: This method should be called only once, when the app is loaded!
        Here we are registering the NutritionGuides_Model and ParentsGuides_Model
        We use the NutritionGuide_Service and ParentGuide_Service to handle the
        business logic for these models. Also, to avoid circular imports, we are
        using the apps.get_model() method to get the model classes that has the 
        purpose of getting the model classes from the tinySteps app so, we can
        register them in the registry and use them in the views and services files.
        """
        NutritionGuides_Model = apps.get_model('tinySteps', 'NutritionGuides_Model')
        ParentsGuides_Model = apps.get_model('tinySteps', 'ParentsGuides_Model')
        
        from .services import NutritionGuide_Service, ParentGuide_Service
        cls.register('nutrition', NutritionGuides_Model, NutritionGuide_Service, 'guides/display')
        cls.register('parent', ParentsGuides_Model, ParentGuide_Service, 'guides/display')

class FactoryRegistry:
    """Registry for all factories in the application"""
    _url_factories = {}
    _service_factories = {}
    
    @classmethod
    def register_url_factory(cls, key, factory_class):
        """Register a URL factory"""
        cls._url_factories[key] = factory_class
        
    @classmethod
    def register_service_factory(cls, key, factory_class):
        """Register a service factory"""
        cls._service_factories[key] = factory_class
        
    @classmethod
    def get_url_factory(cls, key):
        """Get a URL factory by key"""
        return cls._url_factories.get(key)
        
    @classmethod
    def get_service_factory(cls, key):
        """Get a service factory by key"""
        return cls._service_factories.get(key)