from tinySteps.factories import GuideService_Factory
from tinySteps.utils.interfaces.view_interfaces import Template_Resolver, Context_Enhancer

class ServiceBased_Template_Resolver(Template_Resolver):
    """Resolves templates using guide services"""
    
    def __init__(self, factory=None):
        """Initialize with optional factory"""
        self.factory = factory or GuideService_Factory
    
    def get_template_path(self, guide_type, view_type):
        """Return the appropriate template path using a guide service"""
        service = self.factory.create_service(guide_type)
        return service.get_template_path(view_type)

class ServiceBased_Context_Enhancer(Context_Enhancer):
    """Enhances context using guide services"""
    
    def __init__(self, factory=None):
        """Initialize with optional factory"""
        self.factory = factory or GuideService_Factory
    
    def enhance_context(self, context, guide_type, request=None):
        """Add type-specific data using a guide service"""
        service = self.factory.create_service(guide_type)
        return service.get_context_data(context, request)
