import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class EdamamService:
    BASE_URL = 'https://api.edamam.com/api/nutrition-data'
    CACHE_DURATION = 300 # 5min
    
    def __init__(self):
        self.app_id = settings.EDAMAM_APP_ID
        self.app_key = settings.EDAMAM_APP_KEY
    
    # Public methods
    def get_nutrition_data(self, ingredient):
        cache_key = f"edamam_nutrition_{ingredient.replace(' ', '_')}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'ingr': ingredient
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            cache.set(cache_key, data, self.CACHE_DURATION)
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching nutrition data from Edamam: {e}")
            return None
    
    def get_baby_food_nutrition(self, ingredient, baby_age_months=6):
        cache_key = f"edamam_baby_{ingredient.replace(' ', '_')}_{baby_age_months}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'ingr': ingredient,
            'health': self._get_health_tags_for_age(baby_age_months)
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('totalNutrients'):
                if baby_age_months < 6:
                    data['warning'] = 'Foods should be pureed for babies under 6 months'
                elif 6 <= baby_age_months <= 8:
                    data['warning'] = 'Foods should be mashed for babies 6-8 months'
                else:
                    data['warning'] = 'Small soft pieces are appropriate for babies 9+ months'
                
            cache.set(cache_key, data, self.CACHE_DURATION)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching baby nutrition data: {e}")
            return None
    
    # Private methods
    def _get_health_tags_for_age(self, age_months):
        if age_months < 6:
            # Under 6 months - very restricted diet
            return ['baby-food', 'no-added-sugar', 'no-salt']
        elif 6 <= age_months <= 8:
            # 6-8 months - introducing solids
            return ['baby-food', 'no-added-sugar', 'low-salt']
        else:
            # 9+ months - expanding diet
            return ['baby-food', 'low-sugar', 'low-salt']


class NewsAPIService:
    """Service for interacting with the NewsAPI."""
    
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
        
class CurrentsAPI:    
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