from .base_service import Guide_Service
from tinySteps.services.external.nutrition_data_service import NutritionData_Service
from tinySteps.models import ExternalNutritionData_Model, Guides_Model

class NutritionGuide_Service(Guide_Service):
    """Nutrition-specific guide service"""
    
    def __init__(self):
        super().__init__('nutrition')
        self.nutrition_data_service = NutritionData_Service()
    
    def get_template_path(self, view_type):
        """Get the template path for a specific view type"""
        templates = {
            'list': 'guides/display/nutrition_guide_list.html',
            'detail': 'guides/display/nutrition_guide_detail.html',
            'analyzer': 'guides/display/tools/analyzer.html',
            'comparison': 'guides/display/tools/comparison.html',
            'history': 'guides/display/tools/history.html',
            'favorites': 'guides/display/tools/favorites.html',
            'recipe': 'guides/display/tools/recipe.html',
        }
        return templates.get(view_type)
    
    def get_nutrition_data(self, ingredient):
        """Get nutrition data for an ingredient"""
        from tinySteps.services.apis.edamam_service import EdamamAPI_Service
        service = EdamamAPI_Service()
        return service.get_nutrition_data(ingredient)
    
    def analyze_request(self, request):
        """Analyze nutrition request from view"""
        results = None
        ingredient = ''
        error = None
        
        if request.method == 'POST':
            ingredient = request.POST.get('ingredient', '').strip()
            
            if ingredient:
                results = self.get_nutrition_data(ingredient)
                if not results:
                    error = "No nutrition data found for this ingredient. Please try another."
            else:
                error = "Please enter an ingredient to analyze."
        
        recent_guides = self.get_recent_guides(3)
    
        user = request.user if request.user.is_authenticated else None
        saved_data = self.get_saved_nutrition_data(5, user=user)
        
        return {
            'results': results,
            'ingredient': ingredient,
            'error': error,
            'recent_guides': recent_guides,
            'saved_data': saved_data,
        }
    
    def compare_nutrition_data(self, ingredients):
        """Compare nutritional values of different ingredients"""
        results = {}
        
        for ingredient in ingredients:
            data = self.get_nutrition_data(ingredient)
            if data and data.get('totalNutrients'):
                results[ingredient] = data
        
        return results
    
    def save_ingredient_for_user(self, ingredient, user):
        """Save ingredient to the users profile"""
        data = self.get_nutrition_data(ingredient)
        if not data:
            return False
            
        try:
            existing = ExternalNutritionData_Model.objects.filter(
                ingredient__iexact=ingredient
            ).first()
            
            if not existing:
                ExternalNutritionData_Model.objects.create(
                    ingredient=ingredient,
                    data=data
                )
            
            return True
        except Exception:
            return False
    
    def get_popular_ingredients(self, limit=10):
        """Get popular saved ingredients"""
        return ExternalNutritionData_Model.objects.values_list(
            'ingredient', flat=True
        ).order_by('-created_at')[:limit]
    
    def get_saved_nutrition_data(self, limit=5, user=None):
        """Get saved nutrition data for the user"""
        query = ExternalNutritionData_Model.objects.order_by('-created_at')
        
        # Filter by user if provided
        if user and user.is_authenticated:
            query = query.filter(user=user)
        
        return query[:limit]
    
    def get_recent_guides(self, limit=3):
        """Get recent nutrition guides"""
        return self.repository.get_guides_by_type(
            self.guide_type,
            status='approved',
            count=limit
        )
        
    # Métodos de compatibilidad para evitar errores - devuelven valores por defecto
    def get_recent_nutrition_searches(self, limit=5, user=None):
        """Compatibilidad: Devuelve una lista vacía para mantener la API"""
        return []
        
    def get_popular_comparisons(self, limit=5):
        """Compatibilidad: Devuelve datos de ejemplo"""
        return [
            ["apple", "banana"],
            ["broccoli", "spinach"],
            ["yogurt", "milk"],
            ["sweet potato", "carrots"]
        ][:limit]
        
    def save_user_nutrition_preference(self, user, ingredient):
        """Compatibilidad: Redirige a save_ingredient_for_user"""
        return self.save_ingredient_for_user(ingredient, user)
    
    def get_all_guides(self):
        return Guides_Model.objects.filter(guide_type='nutrition')
