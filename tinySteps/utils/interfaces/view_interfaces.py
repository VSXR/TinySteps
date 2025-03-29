from abc import ABC, abstractmethod

class Template_Resolver(ABC):
    """Interface for resolving template paths"""
    
    @abstractmethod
    def get_template_path(self, guide_type, view_type):
        """Return template path for the specified guide and view type"""
        pass

class Context_Enhancer(ABC):
    """Interface for enhancing context data"""
    
    @abstractmethod
    def enhance_context(self, context, guide_type, request=None):
        """Add type-specific data to the context"""
        pass