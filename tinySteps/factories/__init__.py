"""Factories package"""

# Auth Factories
from .auth.auth_factory import AuthUrl_Factory

# Child Factories
from .child.child_factory import ChildUrl_Factory

# Comment Factories
from .comment.comment_factory import CommentUrl_Factory, CommentService_Factory

# Forum Factories
from .forum.forum_factory import ForumUrl_Factory, ForumService_Factory

# Admin Factories
from .admin.admin_factory import AdminUrl_Factory

# Contact Factories
from .contact.contact_factory import ContactUrl_Factory

# Nutrition Factories
from .nutrition.nutrition_factory import NutritionUrl_Factory

# Pages Factories
from .pages.pages_factory import PagesUrl_Factory

# Guide Factories
def get_guide_service_factory():
    from .guide.guide_factory import GuideService_Factory
    return GuideService_Factory

def get_guide_url_factory():
    from .guide.guide_factory import GuideUrl_Factory
    return GuideUrl_Factory

# For backwards compatibility, we expose the factories directly
# (this is what causes circular dependencies but we need to maintain it for now)
try:
    from .guide.guide_factory import GuideUrl_Factory, GuideService_Factory
except ImportError:
    GuideUrl_Factory = None
    GuideService_Factory = None

__all__ = [
    # Auth Factories
    'AuthUrl_Factory',
    
    # Child Factories
    'ChildUrl_Factory',
    
    # Comment Factories
    'CommentUrl_Factory', 'CommentService_Factory',
    
    # Forum Factories
    'ForumUrl_Factory', 'ForumService_Factory',
    
    # Admin Factories
    'AdminUrl_Factory',
    
    # Contact Factories
    'ContactUrl_Factory',
    
    # Nutrition Factories
    'NutritionUrl_Factory',
    
    # Guide Factories
    'GuideUrl_Factory', 'GuideService_Factory', 'get_guide_service_factory', 'get_guide_url_factory',

    # Pages Factories
    'PagesUrl_Factory',
]