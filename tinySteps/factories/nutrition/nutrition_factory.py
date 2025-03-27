from django.urls import path

class NutritionUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for nutrition-specific views"""
        from tinySteps.views.nutrition import analyzer_views
        
        return [
            path('nutrition/history/', analyzer_views.nutrition_history_view, name='nutrition_history'),
            path('nutrition/favorites/', analyzer_views.nutrition_favorites_view, name='nutrition_favorites'),
            path('nutrition/recipe/<int:recipe_id>/', analyzer_views.nutrition_recipe_view, name='nutrition_recipe'),
        ]