from django.shortcuts import render
from tinySteps.factories import GuideService_Factory

def article_list_view(request, category):
    """Generic view for article listings"""
    service = GuideService_Factory.create_service(category)
    
    articles = service.get_articles()
    popular_articles = service.get_popular_articles(limit=3)
    
    base_context = {
        'articles': articles,
        'popular_articles': popular_articles,
        'view_type': 'article_list'
    }
    
    context = service.get_context_data(base_context)
    template = service.get_template_path('article_list')
    
    return render(request, template, context)

def article_detail_view(request, article_id, category):
    """Generic view for article details"""
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