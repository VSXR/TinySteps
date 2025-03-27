from django.shortcuts import get_object_or_404

from tinySteps.models import ExternalNutritionData_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class Nutrition_Repository(GenericRepository):
    """Repository for Nutrition data operations"""
    
    def __init__(self):
        super().__init__(ExternalNutritionData_Model)
    
    def get_by_ingredient(self, ingredient):
        """Get nutrition data for a specific ingredient"""
        return get_object_or_404(self.model, ingredient__iexact=ingredient)
    
    def get_or_none(self, ingredient):
        """Get nutrition data for a specific ingredient or None if not found"""
        try:
            return self.model.objects.get(ingredient__iexact=ingredient)
        except self.model.DoesNotExist:
            return None
    
    def search_ingredients(self, query):
        """Search ingredients by name"""
        return self.model.objects.filter(ingredient__icontains=query)
    
    def get_recent_ingredients(self, limit=10):
        """Get recently added ingredients"""
        return self.model.objects.all().order_by('-created_at')[:limit]
    
    def get_popular_ingredients(self, limit=10):
        """Get popular ingredients (placeholder - we would need view count!)"""
        return self.model.objects.all().order_by('?')[:limit]
    
    def save_nutrition_data(self, ingredient, data):
        """Save nutrition data for an ingredient"""
        nutrition_data, created = self.model.objects.update_or_create(
            ingredient__iexact=ingredient,
            defaults={
                'ingredient': ingredient.lower(),
                'data': data
            }
        )
        return nutrition_data
    
    def compare_nutrition(self, ingredients):
        """Compare nutrition data for multiple ingredients"""
        if not ingredients or len(ingredients) < 2:
            return None
            
        result = {}
        for ingredient in ingredients:
            data = self.get_or_none(ingredient)
            if data:
                result[ingredient] = data.data
                
        return result if result else None