from django.apps import AppConfig
from .registry import GuideType_Registry

class TinyStepsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tinySteps"
    
    def ready(self):
        """Initialize the application"""
        GuideType_Registry.initialize()