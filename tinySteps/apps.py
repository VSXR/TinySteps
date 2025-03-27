from django.apps import AppConfig
from .registry import GuideType_Registry

class TinyStepsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tinySteps"
    
    def ready(self):
        """Initialize the application
        This method is called when the application is ready
        so, we avoid circular imports by importing the registry here!
        """
        GuideType_Registry.initialize()