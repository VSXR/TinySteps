from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from tinySteps.factories import GuideService_Factory

def nutrition_analyzer_view(request):
    """View for nutrition analyzer tool"""
    service = GuideService_Factory.create_service('nutrition')
    
    ingredient = request.GET.get('ingredient', '')
    nutrition_data = None
    
    if ingredient:
        nutrition_data = service.get_nutrition_data(ingredient)
    
    # Usar valores predeterminados vacíos para evitar errores
    recent_searches = []
    popular_ingredients = service.get_popular_ingredients(limit=10)
    
    context = {
        'ingredient': ingredient,
        'nutrition_data': nutrition_data,
        'recent_searches': recent_searches,
        'popular_ingredients': popular_ingredients,
        'section_type': 'nutrition',
        'submit_guide_url': '/guides/submit/',
    }
    
    template = service.get_template_path('analyzer')
    return render(request, template, context)

@login_required
def nutrition_save_view(request):
    """View for saving nutrition data to the users profile"""
    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('nutrition_analyzer')
    
    service = GuideService_Factory.create_service('nutrition')
    ingredient = request.POST.get('ingredient', '')
    
    if ingredient:
        try:
            # Usar el método existente en lugar del eliminado
            success = service.save_ingredient_for_user(ingredient, request.user)
            if success:
                messages.success(request, _("Added to your saved nutrition items!"))
            else:
                messages.warning(request, _("Could not save the ingredient."))
        except AttributeError:
            messages.warning(request, _("Saving nutrition preferences is not available yet."))
    
    return redirect('nutrition_analyzer')

@login_required
def nutrition_history_view(request):
    """View for user's nutrition search history"""
    service = GuideService_Factory.create_service('nutrition')
    
    context = {
        'section_type': 'nutrition',
        'submit_guide_url': '/guides/submit/',
    }
    
    template = service.get_template_path('history')
    return render(request, template, context)

@login_required
def nutrition_favorites_view(request):
    """View for user's favorite nutrition items"""
    service = GuideService_Factory.create_service('nutrition')
    
    context = {
        'section_type': 'nutrition',
        'submit_guide_url': '/guides/submit/',
    }
    
    template = service.get_template_path('favorites')
    return render(request, template, context)

@login_required
def nutrition_recipe_view(request, recipe_id):
    """View for nutrition recipe details"""
    service = GuideService_Factory.create_service('nutrition')
    
    context = {
        'section_type': 'nutrition',
        'submit_guide_url': '/guides/submit/',
        'recipe_id': recipe_id
    }
    
    template = service.get_template_path('recipe')
    return render(request, template, context)