from datetime import datetime
from django.core.cache import cache
from django.db.models import Q
from tinySteps.models import ExternalArticle_Model

class Article_Service:
    """Service for managing external articles"""
    
    CACHE_PREFIX = "articles_"
    CACHE_DURATION = 3600  # 1 hour
    
    @staticmethod
    def get_articles_by_category(category, limit=None):
        """Get articles by category with optional limit"""
        cache_key = f"{Article_Service.CACHE_PREFIX}{category}_{'all' if limit is None else limit}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        query = ExternalArticle_Model.objects.filter(
            category=category
        ).order_by('-published_at')
        
        if limit:
            query = query[:limit]
        
        # Cache the result
        articles = list(query)
        cache.set(cache_key, articles, Article_Service.CACHE_DURATION)
        
        return articles
    
    @staticmethod
    def get_article_by_id(article_id):
        """Get a specific article by ID"""
        cache_key = f"{Article_Service.CACHE_PREFIX}id_{article_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            article = ExternalArticle_Model.objects.get(id=article_id)
            cache.set(cache_key, article, Article_Service.CACHE_DURATION)
            return article
        except ExternalArticle_Model.DoesNotExist:
            return None
    
    @staticmethod
    def search_articles(query, category=None):
        """Search articles by query string and optional category"""
        search_query = Q(title__icontains=query) | Q(description__icontains=query)
        
        if category:
            search_query &= Q(category=category)
        
        return ExternalArticle_Model.objects.filter(search_query).order_by('-published_at')
    
    @staticmethod
    def update_from_apis(topic=None):
        """Update articles from external APIs"""
        from tinySteps.services.apis.news_service import NewsAPI_Service
        from tinySteps.services.apis.currents_service import CurrentsAPI_Service
        
        news_service = NewsAPI_Service()
        currents_service = CurrentsAPI_Service()
        
        if topic:
            articles = news_service.get_parenting_articles_by_topic(topic, force_refresh=True)
            news = currents_service.get_news_by_topic(topic, force_refresh=True)
        else:
            articles = news_service.get_parenting_articles(force_refresh=True)
            news = currents_service.get_news_by_topic('nutrition', force_refresh=True)
        
        if articles:
            Article_Service._update_articles(articles)

        if news:
            Article_Service._update_news(news)
        
        return True
    
    @staticmethod
    def _update_articles(articles):
        """Private method to update articles from NewsAPI"""
        for article in articles:
            try:
                # Extract relevant data
                title = article.get('title', '')
                source = article.get('source', {}).get('name', 'Unknown')
                url = article.get('url', '')
                published_at_str = article.get('publishedAt', '')
                
                # Parse the date
                if published_at_str:
                    try:
                        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    except ValueError:
                        published_at = datetime.now()
                else:
                    published_at = datetime.now()
                
                # Create or update the article
                ExternalArticle_Model.objects.update_or_create(
                    url=url,
                    defaults={
                        'title': title,
                        'source': source,
                        'published_at': published_at,
                        'api_source': 'NewsAPI'
                    }
                )
            except Exception as e:
                print(f"Error updating article: {e}")
    
    @staticmethod
    def _update_news(news_items):
        """Private method to update news from CurrentsAPI"""
        for item in news_items:
            try:
                # Extract relevant data
                title = item.get('title', '')
                source = item.get('author', 'Unknown')
                url = item.get('url', '')
                published_at_str = item.get('published', '')
                
                # Parse the date
                if published_at_str:
                    try:
                        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    except ValueError:
                        published_at = datetime.now()
                else:
                    published_at = datetime.now()
                
                # Create or update the article
                ExternalArticle_Model.objects.update_or_create(
                    url=url,
                    defaults={
                        'title': title,
                        'source': source,
                        'published_at': published_at,
                        'api_source': 'CurrentsAPI'
                    }
                )
            except Exception as e:
                print(f"Error updating news item: {e}")