from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.db import DatabaseError
import logging

from ..factories import GuideService_Factory

logger = logging.getLogger(__name__)

def nutrition_analyzer_view(request, service=None):
    nutrition_service = service or GuideService_Factory.create_service('nutrition')
    results = None
    ingredient = ''
    error = None
    
    try:
        if request.method == 'POST':
            ingredient = request.POST.get('ingredient', '').strip()
            
            if ingredient:
                results = nutrition_service.get_nutrition_data(ingredient)
                if not results:
                    error = _("No nutrition data found for this ingredient. Please try another.")
            else:
                error = _("Please enter an ingredient to analyze.")
        
        recent_guides = nutrition_service.get_recent_guides(3)
        saved_data = nutrition_service.get_saved_nutrition_data(5)
    
    except DatabaseError as e:
        error = _("Database error. Please try again later.")
        logger.error(f"Database error in nutrition analyzer: {e}")
        recent_guides = []
        saved_data = []
    except Exception as e:
        error = _("An unexpected error occurred. Please try again later.")
        logger.error(f"Error in nutrition analyzer: {e}")
        recent_guides = []
        saved_data = []
    
    context = {
        'results': results,
        'ingredient': ingredient,
        'error': error,
        'recent_guides': recent_guides,
        'saved_data': saved_data,
    }
    
    template = nutrition_service.get_template_path('analyzer')
    return render(request, template, context)

def nutrition_comparison_view(request):
    """View for comparing nutritional values of different ingredients"""
    nutrition_service = GuideService_Factory.create_service('nutrition')
    
    try:
        ingredients = request.GET.getlist('ingredients', [])
        results = {}
        error = None
        
        if ingredients:
            results = nutrition_service.compare_ingredients(ingredients)
            if not results:
                error = _("Could not find nutrition data for some ingredients")
        
        popular_ingredients = nutrition_service.get_popular_ingredients(10)
        context = {
            'results': results,
            'ingredients': ingredients,
            'error': error,
            'popular_ingredients': popular_ingredients
        }
        
        template = nutrition_service.get_template_path('comparison')
        return render(request, template, context)
    
    except Exception as e:
        logger.error(f"Error in nutrition comparison: {e}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error processing nutrition comparison"))

def nutrition_save_view(request, ingredient):
    """View for saving nutrition data to user profile - SRP"""
    if not request.user.is_authenticated:
        from django.contrib import messages
        messages.warning(request, _("Please log in to save nutrition data"))
        return redirect('login')
    
    nutrition_service = GuideService_Factory.create_service('nutrition')
    try:
        success = nutrition_service.save_ingredient_for_user(ingredient, request.user)
        if success:
            messages.success(request, _("Ingredient saved to your profile"))
        else:
            messages.error(request, _("Could not save ingredient. Please try again."))
        
        return redirect(f'/guides/nutrition/analyzer/?ingredient={ingredient}')
    
    except Exception as e:
        logger.error(f"Error saving nutrition data: {e}")
        from .error_views import database_error_view
        return database_error_view(request, _("Error saving nutrition data."))