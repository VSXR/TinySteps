from tinySteps.utils.helpers.view_helpers import ServiceBased_Template_Resolver, ServiceBased_Context_Enhancer

class Guide_ViewHelper:
    """Helper class for guide views"""
    
    def __init__(self, template_resolver=None, context_enhancer=None):
        """Initialize with optional resolver and enhancer"""
        self.template_resolver = template_resolver or ServiceBased_Template_Resolver()
        self.context_enhancer = context_enhancer or ServiceBased_Context_Enhancer()
    
    def get_template(self, guide_type, view_type):
        """Return the appropriate template path"""
        return self.template_resolver.get_template_path(guide_type, view_type)
    
    def enhance_context(self, context, guide_type, request=None):
        """Add type-specific data to the context"""
        return self.context_enhancer.enhance_context(context, guide_type, request)
    
    @classmethod
    def create_default(cls):
        """Create an instance with default components"""
        return cls()

# Default instance for backward compatibility!!
# This is a singleton instance of the Guide_ViewHelper class, 
# initialized with default template resolver and context enhancer
_default_helper = Guide_ViewHelper.create_default()

def get_template(guide_type, view_type):
    """Get the template path for a specific guide type and view type"""
    return _default_helper.get_template(guide_type, view_type)
    
def enhance_context(context, guide_type, request=None):
    """Enhance the context with additional data for a specific guide type"""
    return _default_helper.enhance_context(context, guide_type, request)