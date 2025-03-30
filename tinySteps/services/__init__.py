"""Service package"""

# Core services
from tinySteps.services.core.admin_service import AdminGuide_Service, Notification_Repository
from tinySteps.services.core.child_service import Child_Service
from tinySteps.services.core.forum_service import Forum_Service

# Guide services
from tinySteps.services.guides.base_service import Guide_Service
from tinySteps.services.guides.context_service import GuideContext_Service
from tinySteps.services.guides.nutrition_service import NutritionGuide_Service
from tinySteps.services.guides.parent_service import ParentGuide_Service

# External data services
from tinySteps.services.external.article_service import Article_Service
from tinySteps.services.external.nutrition_data_service import NutritionData_Service

# API integrations
from tinySteps.services.apis.currents_service import CurrentsAPI_Service
from tinySteps.services.apis.edamam_service import EdamamAPI_Service
from tinySteps.services.apis.news_service import NewsAPI_Service

# Communication services
from tinySteps.services.communication.contact_service import Contact_Service

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