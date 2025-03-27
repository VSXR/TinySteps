from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from tinySteps.services.guides.context_service import GuideContext_Service
from tinySteps.utils.helpers.helpers import Guide_ViewHelper
from tinySteps.factories import GuideService_Factory

def guides_page(request):
    """Main guides page view"""
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
    """Generic view for guide details"""
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

@login_required
def my_guides(request):
    """Users guides view"""
    service = GuideService_Factory.create_service('parent')
    guides = service.get_user_guides(request.user)
    
    context = {
        'guides': guides,
        'is_staff': request.user.is_staff
    }
    
    return render(request, 'guides/my_guides.html', context)