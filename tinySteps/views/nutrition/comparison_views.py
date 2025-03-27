from django.shortcuts import render
from tinySteps.factories import GuideService_Factory

def nutrition_comparison_view(request):
    """View for comparing nutrition data of multiple ingredients"""
    service = GuideService_Factory.create_service('nutrition')
    
    ingredients = request.GET.getlist('ingredients', [])
    comparison_data = None
    
    if ingredients and len(ingredients) > 1:
        comparison_data = service.compare_nutrition_data(ingredients)
    
    context = {
        'ingredients': ingredients,
        'comparison_data': comparison_data,
        'popular_comparisons': service.get_popular_comparisons(limit=5)
    }
    
    template = service.get_template_path('comparison')
    return render(request, template, context)