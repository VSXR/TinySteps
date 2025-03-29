from tinySteps.utils.helpers.guides_helper import get_template, enhance_context

class Guide_ViewHelper:
    """Helper class for guide views"""
    
    @staticmethod
    def get_template(guide_type, view_type):
        """Return the appropriate template path based on guide type and view type"""
        return get_template(guide_type, view_type)
    
    @staticmethod
    def enhance_context(context, guide_type, request=None):
        """Add type-specific data to the context"""
        return enhance_context(context, guide_type, request)