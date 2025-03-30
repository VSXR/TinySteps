from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from tinySteps.services.guides.context_service import GuideContext_Service
from tinySteps.utils.helpers.guides_helper import Guide_ViewHelper
from tinySteps.factories import GuideService_Factory

view_helper = Guide_ViewHelper.create_default()

def guides_page(request):
    """Main guides page view"""
    context_service = GuideContext_Service()
    context = context_service.get_guides_page_context()
    
    parent_service = GuideService_Factory.create_service('parent')
    nutrition_service = GuideService_Factory.create_service('nutrition')
    
    context['all_parent_guides'] = parent_service.get_guide_listing()
    context['all_nutrition_guides'] = nutrition_service.get_guide_listing()
    context['submit_guide_url'] = '/guides/submit/'
    
    return render(request, 'guides/index.html', context)

def guide_list_view(request, guide_type):
    """View for listing guides of a specific type"""
    try:
        service = GuideService_Factory.create_service(guide_type)
        if not service:
            raise ValueError(_("Invalid guide type."))
        
        template = view_helper.get_template(guide_type, 'list')
        guides = service.get_recent_guides(10)
        
        context = {
            'guides': guides,
            'guide_type': guide_type,
            'view_type': 'list',
            'submit_guide_url': '/guides/submit/',
            'section_type': guide_type
        }
        
        context = view_helper.enhance_context(context, guide_type, request)
        return render(request, template, context)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')
    
def guide_detail_view(request, pk, guide_type=None):
    """View for displaying a specific guide's details"""
    try:
        service = GuideService_Factory.create_service(guide_type)
        if not service:
            raise ValueError(_("Invalid guide type."))
        
        guide = service.get_guide_detail(pk)
        if not guide:
            raise ValueError(_("Guide not found."))
        
        related_guides = service.get_related_guides(pk, limit=3)
        comments = service.get_guide_comments(pk)
        template = view_helper.get_template(guide_type, 'detail')
        
        context = {
            'guide': guide,
            'related_guides': related_guides,
            'comments': comments,
            'guide_type': guide_type,
            'view_type': 'detail',
            'section_type': guide_type
        }
        
        context = view_helper.enhance_context(context, guide_type, request)
        return render(request, template, context)
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')
    
def my_guides_view(request):
    """View for displaying the user's guides"""
    try:
        if not request.user.is_authenticated:
            messages.warning(request, _("You must be logged in to view your guides"))
            return redirect('login')
        
        parent_service = GuideService_Factory.create_service('parent')
        nutrition_service = GuideService_Factory.create_service('nutrition')
        
        parent_guides = parent_service.get_user_guides(request.user)
        nutrition_guides = nutrition_service.get_user_guides(request.user)
        
        all_guides = list(parent_guides) + list(nutrition_guides)
        all_guides.sort(key=lambda x: x.created_at, reverse=True)
        
        context = {
            'guides': all_guides,
            'title': _('My Guides'),
            'section': 'guides',
            'submit_guide_url': '/guides/submit/',
            'section_type': 'my_guides'
        }
        
        return render(request, 'guides/my_guides.html', context)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('guides')