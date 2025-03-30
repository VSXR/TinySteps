from django.shortcuts import render
from tinySteps.factories import GuideService_Factory

def article_list_view(request, guide_type):
    """Generic view for article listings"""
    service = GuideService_Factory.create_service(guide_type)
    
    articles = service.get_articles()
    popular_articles = service.get_popular_articles(limit=3)
    
    base_context = {
        'articles': articles,
        'popular_articles': popular_articles,
        'view_type': 'article_list',
        'submit_guide_url': '/guides/submit/',
        'section_type': guide_type
    }
    
    context = service.get_context_data(base_context)
    template = service.get_template_path('articles')
    
    return render(request, template, context)

def article_detail_view(request, article_id, category, guide_type=None):
    """Generic view for article details"""
    service_type = guide_type if guide_type else category
    service = GuideService_Factory.create_service(service_type)
    
    article = service.get_article_detail(article_id)
    related_articles = service.get_articles(limit=3)
    related_guides = service.get_guide_listing(limit=3)
    
    base_context = {
        'article': article,
        'related_articles': related_articles,
        'related_guides': related_guides,
        'view_type': 'article_detail',
        'submit_guide_url': '/guides/submit/',
        'section_type': service_type  # Use consistent type
    }
    
    context = service.get_context_data(base_context, request)
    template = service.get_template_path('article_detail')
    
    return render(request, template, context)