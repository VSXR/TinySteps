from .registry import GuideType_Registry
from .factories import GuideService_Factory

class Guide_ViewHelper:
    """Helper class for guide views implementing DIP & OCP"""
    
    @staticmethod
    def get_template(guide_type, view_type):
        """Return the appropriate template path based on guide type and view type"""
        service = GuideService_Factory.create_service(guide_type)
        return service.get_template_path(view_type)
    
    @staticmethod
    def enhance_context(context, guide_type, request=None):
        """Add type-specific data to the context"""
        service = GuideService_Factory.create_service(guide_type)
        return service.get_context_data(context, request)
    
