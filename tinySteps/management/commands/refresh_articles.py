from django.core.management.base import BaseCommand
from tinySteps.services import NewsAPIService, CurrentsAPI
from tinySteps.models import ExternalArticle_Model
from django.utils import timezone

class Command(BaseCommand):
    help = 'Updates news articles from external APIs'
    
    def handle(self, *args, **options):
        self.stdout.write('Updating news articles...')
        
        news_service = NewsAPIService()
        currents_service = CurrentsAPI()
        articles = news_service.get_parenting_articles(force_refresh=True)
        news = currents_service.get_first_time_parent_news(force_refresh=True)
        
        # Guardar artículos en la base de datos
        if articles and 'articles' in articles:
            for article in articles['articles']:
                ExternalArticle_Model.objects.update_or_create(
                    source_id=article.get('url', ''),
                    defaults={
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'url': article.get('url', ''),
                        'image_url': article.get('urlToImage', ''),
                        'published_at': article.get('publishedAt', timezone.now())
                    }
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully updated news articles'))