from django.core.cache import cache
from ..models import ExternalNutritionData_Model

class NutritionData_Service:
    """Service for accessing nutrition data following SRP"""
    
    CACHE_PREFIX = "nutrition_data_"
    CACHE_DURATION = 86400  # 24 hours
    
    @staticmethod
    def get_ingredient_data(ingredient):
        """Get nutrition data for an ingredient"""
        cache_key = f"{NutritionData_Service.CACHE_PREFIX}{ingredient.lower()}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Try to get from database
        try:
            nutrition_data = ExternalNutritionData_Model.objects.get(ingredient__iexact=ingredient)
            cache.set(cache_key, nutrition_data.data, NutritionData_Service.CACHE_DURATION)
            return nutrition_data.data
        except ExternalNutritionData_Model.DoesNotExist:
            # Try to get it from external API but import it here to avoid circular imports
            from .edemanAPI_service import EdamamAPI_Service
            api_service = EdamamAPI_Service()
            data = api_service.get_nutrition_data(ingredient, force_refresh=True)  # Force refresh to avoid infinite recursion
            
            if data and data.get('totalNutrients'):
                # No need to store in DB since the API service already does that
                return data
            return None
    
    @staticmethod
    def update_ingredient_data(ingredient, data):
        """Update or create nutrition data for an ingredient"""
        obj, _ = ExternalNutritionData_Model.objects.update_or_create(
            ingredient__iexact=ingredient,
            defaults={
                'ingredient': ingredient,
                'data': data
            }
        )
        
        # Update cache
        cache_key = f"{NutritionData_Service.CACHE_PREFIX}{ingredient.lower()}"
        cache.set(cache_key, data, NutritionData_Service.CACHE_DURATION)
        
        return obj
    
    @staticmethod
    def get_all_ingredients():
        """Get all available ingredients"""
        return ExternalNutritionData_Model.objects.values_list('ingredient', flat=True)