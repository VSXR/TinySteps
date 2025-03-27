"""
Command to refresh news articles from external APIs
"""
import argparse
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from tinySteps.services.apis import NewsAPI_Service, CurrentsAPI_Service
from tinySteps.models import ExternalArticle_Model

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates news articles from external APIs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', 
            type=int, 
            default=10,
            help='Maximum number of articles to fetch from each source'
        )
        parser.add_argument(
            '--force', 
            action='store_true',
            help='Force refresh even if cache is valid'
        )
        parser.add_argument(
            '--clear', 
            action='store_true',
            help='Clear existing articles before fetching new ones'
        )
    
    def handle(self, *args, **options):
        limit = options.get('limit', 10)
        force = options.get('force', False)
        clear = options.get('clear', False)
        
        self.stdout.write('Updating news articles...')
        
        # Clear existing articles if requested
        if clear:
            count = ExternalArticle_Model.objects.all().count()
            ExternalArticle_Model.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Cleared {count} existing articles'))
        
        # Initialize services
        news_service = NewsAPI_Service()
        currents_service = CurrentsAPI_Service()
        
        # Fetch articles
        try:
            articles = news_service.get_parenting_articles(
                force_refresh=force, 
                limit=limit
            )
            self.stdout.write(f'Fetched {len(articles.get("articles", []))} articles from NewsAPI')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching from NewsAPI: {str(e)}'))
            articles = {'articles': []}
        
        try:
            news = currents_service.get_first_time_parent_news(
                force_refresh=force,
                limit=limit
            )
            self.stdout.write(f'Fetched {len(news.get("news", []))} articles from CurrentsAPI')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching from CurrentsAPI: {str(e)}'))
            news = {'news': []}
        
        # Save articles from NewsAPI
        articles_saved = 0
        if articles and 'articles' in articles:
            for article in articles['articles']:
                try:
                    ExternalArticle_Model.objects.update_or_create(
                        source_id=article.get('url', ''),
                        defaults={
                            'title': article.get('title', ''),
                            'summary': article.get('description', ''),
                            'url': article.get('url', ''),
                            'image_url': article.get('urlToImage', ''),
                            'published_at': article.get('publishedAt', timezone.now()),
                            'source_name': article.get('source', {}).get('name', 'NewsAPI')
                        }
                    )
                    articles_saved += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error saving article: {str(e)}'))
        
        # Save articles from CurrentsAPI
        if news and 'news' in news:
            for item in news['news']:
                try:
                    ExternalArticle_Model.objects.update_or_create(
                        source_id=item.get('url', ''),
                        defaults={
                            'title': item.get('title', ''),
                            'summary': item.get('description', ''),
                            'url': item.get('url', ''),
                            'image_url': item.get('image', ''),
                            'published_at': item.get('published', timezone.now()),
                            'source_name': item.get('source', {}).get('name', 'CurrentsAPI')
                        }
                    )
                    articles_saved += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error saving article: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {articles_saved} news articles'))

def main(args=None):
    """Run the command with the given arguments."""
    parser = argparse.ArgumentParser(description='Update news articles from external APIs')
    parser.add_argument(
        '--limit', 
        type=int, 
        default=10,
        help='Maximum number of articles to fetch from each source'
    )
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Force refresh even if cache is valid'
    )
    parser.add_argument(
        '--clear', 
        action='store_true',
        help='Clear existing articles before fetching new ones'
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Try to import Django models and run as Django command
        from django.core.management import call_command
        call_command('refresh_articles', 
                    limit=parsed_args.limit,
                    force=parsed_args.force,
                    clear=parsed_args.clear)
    except ImportError:
        logger.error("This command requires Django to be available.")
        return 1

if __name__ == '__main__':
    main()