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
    
    context = {
        'ingredient': ingredient,
        'nutrition_data': nutrition_data,
        'recent_searches': service.get_recent_nutrition_searches(limit=5),
        'popular_ingredients': service.get_popular_ingredients(limit=10),
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
        service.save_user_nutrition_preference(request.user, ingredient)
        messages.success(request, _("Added to your saved nutrition items!"))
    
    return redirect('nutrition_analyzer')