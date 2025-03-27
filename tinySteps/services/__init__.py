"""Service package"""

# Core services
from .core.admin_service import AdminGuide_Service, Notification_Repository
from .core.child_service import Child_Service
from .core.forum_service import Forum_Service

# Guide services
from .guides.base_service import Guide_Service
from .guides.context_service import GuideContext_Service
from .guides.nutrition_service import NutritionGuide_Service
from .guides.parent_service import ParentGuide_Service

# External data services
from .external.article_service import Article_Service
from .external.nutrition_data_service import NutritionData_Service

# API integrations
from .apis.currents_service import CurrentsAPI_Service
from .apis.edamam_service import EdamamAPI_Service
from .apis.news_service import NewsAPI_Service

# Communication services
from .communication.contact_service import Contact_Service

__all__ = [
    'AdminGuide_Service',
    'Article_Service',
    'Child_Service',
    'Contact_Service',
    'CurrentsAPI_Service',
    'EdamamAPI_Service',
    'Forum_Service',
    'Guide_Service',
    'GuideContext_Service',
    'NewsAPI_Service',
    'Notification_Repository',
    'NutritionData_Service',
    'NutritionGuide_Service',
    'ParentGuide_Service'
]