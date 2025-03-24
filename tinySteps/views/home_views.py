from django.shortcuts import render
from ..services.guide_context_service import GuideContext_Service

def index(request):
    """Home page view using service layer for DIP"""
    context_service = GuideContext_Service()
    context = context_service.get_index_page_context()
    
    return render(request, 'pages/index.html', context)

def about(request):
    """About page view"""
    return render(request, 'pages/about.html')

def page_not_found(request, exception=None):
    """404 page view"""
    return render(request, 'pages/404.html', status=404)