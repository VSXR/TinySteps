import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class NewsAPI_Service:
    """Service for interacting with the NewsAPI"""
    
    BASE_URL = 'https://newsapi.org/v2/everything'
    CACHE_DURATION = 300  # 5 minutes in seconds
    
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
    
    # Public methods
    def get_parenting_articles(self, query="\"first-time parents\" OR \"new parents\" OR \"newborn care\" OR \"infant development\" OR \"baby milestones\"", page=1, page_size=10, force_refresh=True):
        return self._get_articles('parenting', query, page, page_size, force_refresh)
    
    def get_nutrition_articles(self, query=None, page=1, page_size=10, force_refresh=True):
        if query is None:
            query = (
                "\"baby food\" OR \"infant nutrition\" OR \"first foods\" OR "
                "\"introducing solids\" OR \"breastfeeding tips\" OR \"formula feeding\" OR "
                "\"homemade baby food\" OR \"baby meal planning\" OR \"age-appropriate foods\""
            )
        return self._get_articles('nutrition', query, page, page_size, force_refresh)
    
    def get_parenting_articles_by_topic(self, topic, page=1, page_size=10, force_refresh=True):
        topic_queries = {
            'newborn': '"newborn care" OR "first month" OR "newborn sleep" OR "newborn feeding"',
            'sleep': '"baby sleep" OR "infant sleep" OR "sleep training" OR "sleep schedule"',
            'development': '"baby milestones" OR "infant development" OR "baby growth" OR "developmental stages"',
            'health': '"baby health" OR "infant healthcare" OR "common baby illnesses" OR "baby doctor visits"',
            'solids': '"introducing solids" OR "baby first foods" OR "baby led weaning" OR "infant nutrition"',
            'first_time': '"first time parent" OR "new parent" OR "first baby" OR "new to parenting"',
            'routines': '"baby routines" OR "infant schedule" OR "baby daily routine" OR "newborn schedule"',
            'postpartum': '"postpartum recovery" OR "after childbirth" OR "new mom health" OR "postpartum care"',
            'safety': '"baby-proofing" OR "infant safety" OR "baby safety tips" OR "new parent safety"'
        }
        
        query = topic_queries.get(topic.lower(), '"first-time parents" OR "baby care"')
        return self._get_articles(f'parenting_{topic.lower()}', query, page, page_size, force_refresh)
    
    # Private methods
    def _get_articles(self, category, query, page=1, page_size=10, force_refresh=False):
        cache_key = f"newsapi_{category}_{query.replace(' ', '_')}_{page}_{page_size}"
        cached_data = None if force_refresh else cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        params = {
            'apiKey': self.api_key,
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'page': page,
            'pageSize': page_size
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            cache.set(cache_key, data, self.CACHE_DURATION)
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news articles: {e}")
            return None