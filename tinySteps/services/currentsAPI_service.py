import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class CurrentsAPI_Service:
    BASE_URL = 'https://api.currentsapi.services/v1/latest-news'
    CACHE_DURATION = 300  # 5min
    
    def __init__(self):
        self.api_key = settings.CURRENTS_API_KEY
    
    # Public methods
    def get_first_time_parent_news(self, page=1, page_size=10, force_refresh=True):
        return self._get_news('first-time parents', page, page_size, force_refresh)
        
    def get_parenting_tips(self, page=1, page_size=10, force_refresh=True):
        return self._get_news('parenting tips', page, page_size, force_refresh)
        
    def get_baby_development_news(self, page=1, page_size=10, force_refresh=True):
        return self._get_news('baby development', page, page_size, force_refresh)
    
    def get_news_by_topic(self, topic, page=1, page_size=10, force_refresh=True):
        topics = {
            'newborn': 'newborn care',
            'sleep': 'baby sleep',
            'development': 'baby milestones',
            'health': 'baby health',
            'solids': 'introducing solids',
            'first_time': 'first-time parents',
            'routines': 'baby routines',
            'postpartum': 'postpartum recovery',
            'safety': 'baby safety'
        }
        search_term = topics.get(topic, 'first-time parents')
        return self._get_news(search_term, page, page_size, force_refresh)
    
    # Private methods
    def _get_news(self, search_term, page=1, page_size=10, force_refresh=True):
        cache_key = f"currents_{search_term.replace(' ', '_')}_{page}_{page_size}"
        cached_data = None if force_refresh else cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        params = {
            'apiKey': self.api_key,
            'language': 'en',
            'category': search_term,
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
            logger.error(f"Error fetching news articles from Currents API: {e}")
            return None