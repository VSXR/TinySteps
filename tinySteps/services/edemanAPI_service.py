import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class EdamamAPI_Service:
    """Service for interacting with Edamam Nutrition API"""
    
    BASE_URL = "https://api.edamam.com/api/nutrition-data"
    CACHE_PREFIX = "edamam_"
    CACHE_DURATION = 604800  # 1 week
    
    def __init__(self):
        self.app_id = settings.EDAMAM_APP_ID
        self.app_key = settings.EDAMAM_APP_KEY
    
    def get_nutrition_data(self, ingredient, force_refresh=False):
        """Get nutrition data for an ingredient"""
        # Check if we already have this data saved - use delayed import to avoid circular reference
        if not force_refresh:
            from .nutrition_data_service import NutritionData_Service
            existing_data = NutritionData_Service.get_ingredient_data(ingredient)
            if existing_data:
                return existing_data
        
        # If not, fetch from API
        cache_key = f"{self.CACHE_PREFIX}{ingredient.lower()}"
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'ingr': ingredient
            }
            
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Save to database and cache - use delayed import to avoid circular reference
            from .nutrition_data_service import NutritionData_Service
            NutritionData_Service.update_ingredient_data(ingredient, data)
            
            cache.set(cache_key, data, self.CACHE_DURATION)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching nutrition data for {ingredient}: {str(e)}")
            return None