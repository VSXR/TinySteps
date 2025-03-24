from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from ..services.guide_context_service import GuideContext_Service
from ..helpers import Guide_ViewHelper
from ..forms import GuideSubmission_Form
from ..factories import GuideService_Factory

def guides_page(request):
    """Main guides page view using service layer for DIP"""
    context_service = GuideContext_Service()
    context = context_service.get_guides_page_context()
    
    return render(request, 'guides/index.html', context)

def get_guide_service(guide_type):
    """Get a guide service instance for the given type"""
    return GuideService_Factory.create_service(guide_type)

def guide_list_view(request, guide_type):
    """View for listing guides of a specific type"""
    try:
        service = get_guide_service(guide_type)
        
        template = Guide_ViewHelper.get_template(guide_type, 'list')
        guides = service.get_recent_guides(10)
        articles = service.get_articles_by_type(guide_type)[:3]
        
        context = {
            'guides': guides,
            'recent_articles': articles,
            'guide_type': guide_type
        }
        
        context = Guide_ViewHelper.enhance_context(context, guide_type, request)
        
        return render(request, template, context)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')

def guide_detail_view(request, pk, guide_type):
    """Generic view for guide details using service layer for DIP"""
    service = GuideService_Factory.create_service(guide_type)
    guide = service.get_guide_detail(pk)
    comments = service.get_guide_comments(pk)
    related_guides = service.get_related_guides(pk)
    
    base_context = {
        'guide': guide,
        'comments': comments,
        'related_guides': related_guides,
        'view_type': 'detail'
    }
    
    context = service.get_context_data(base_context)
    template = service.get_template_path('detail')
    
    return render(request, template, context)

def article_list_view(request, category):
    """Generic view for article listings using service layer for DIP"""
    service = GuideService_Factory.create_service(category)
    page_num = int(request.GET.get('page', 1))  # Renamed to avoid warning
    topic = request.GET.get('topic', '')
    
    articles = service.get_articles(topic=topic)
    related_guides = service.get_guide_listing(limit=3)
    
    base_context = {
        'articles': articles,
        'related_guides': related_guides,
        'topic': topic,
        'view_type': 'articles',
        'page': page_num  # Add to context to use it
    }
    
    context = service.get_context_data(base_context, request)
    template = service.get_template_path('articles')
    
    return render(request, template, context)

def article_detail_view(request, article_id, category):
    """Generic view for article details using service layer for DIP"""
    service = GuideService_Factory.create_service(category)
    
    article = service.get_article_detail(article_id)
    related_articles = service.get_articles(limit=3)
    related_guides = service.get_guide_listing(limit=3)
    
    base_context = {
        'article': article,
        'related_articles': related_articles,
        'related_guides': related_guides,
        'view_type': 'article_detail'
    }
    
    context = service.get_context_data(base_context)
    template = service.get_template_path('article_detail')
    
    return render(request, template, context)

@login_required
def my_guides(request):
    """User's guides view"""
    service = GuideService_Factory.create_service('parent')  # Any guide type works here
    guides = service.get_user_guides(request.user)
    
    context = {
        'guides': guides,
        'is_staff': request.user.is_staff
    }
    
    return render(request, 'guides/my_guides.html', context)

class SubmitGuide_View(LoginRequiredMixin, View):
    """Guide submission view implementing SRP and DIP"""
    
    def get(self, request, guide_type=None):
        """Handle GET request - show form"""
        if not guide_type:
            guide_type = 'parent'
        
        form = GuideSubmission_Form()
        return render(request, 'guides/submit.html', {
            'form': form,
            'guide_type': guide_type
        })
    
    def post(self, request, guide_type=None):
        """Handle POST request - process form"""
        if not guide_type:
            guide_type = 'parent'
        
        form = GuideSubmission_Form(request.POST, request.FILES)
        if form.is_valid():
            service = GuideService_Factory.create_service(guide_type)
            created_guide = service.create_guide_from_form(form, request.user)  # Renamed to avoid warning
            messages.success(request, _("Your guide has been submitted for review!"))
            return redirect('my_guides')
        
        return render(request, 'guides/submit.html', {
            'form': form,
            'guide_type': guide_type
        })

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

def nutrition_comparison_view(request):
    """View for comparing nutrition data of multiple ingredients"""
    service = GuideService_Factory.create_service('nutrition')
    
    ingredients = request.GET.getlist('ingredients', [])
    comparison_data = {}
    
    if ingredients:
        for ingredient in ingredients:
            comparison_data[ingredient] = service.get_nutrition_data(ingredient)
    
    context = {
        'ingredients': ingredients,
        'comparison_data': comparison_data,
        'popular_ingredients': service.get_popular_ingredients(limit=10),
    }
    
    template = service.get_template_path('comparison')
    return render(request, template, context)

def nutrition_save_view(request):
    """View for saving nutrition data to user's profile"""
    if request.method != 'POST' or not request.user.is_authenticated:
        return redirect('nutrition_analyzer')
    
    service = GuideService_Factory.create_service('nutrition')
    ingredient = request.POST.get('ingredient', '')
    
    if ingredient:
        service.save_user_nutrition_preference(request.user, ingredient)
        messages.success(request, _("Added to your saved nutrition items!"))
    
    return redirect('nutrition_analyzer')

def submit_guide(request, guide_type=None):
    """Function-based view wrapper for SubmitGuide_View"""
    view = SubmitGuide_View.as_view()
    return view(request, guide_type=guide_type)