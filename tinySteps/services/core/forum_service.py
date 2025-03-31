from django.contrib.contenttypes.models import ContentType
from tinySteps.models import ParentsForum_Model, Comment_Model
from tinySteps.repositories import Forum_Repository
from django.db.models import Count

class Forum_Service:
    """Service for forum operations"""
    
    def __init__(self, repository=None):
        self.repository = repository or Forum_Repository()
    
    def search_posts(self, search_term, category=None):
        """Search for posts by title or description with optional category filter"""
        if category:
            return self.repository.search_posts(search_term, category)
        else:
            return self.repository.search_posts(search_term)

    # Post retrieval methods
    def get_posts(self, page=1, search=None, category=None, per_page=10):
        """Get forum posts with optional filtering"""
        if search:
            posts = self.repository.search_posts(search, category)
        elif category:
            posts = self.repository.get_posts_by_category(category)
        else:
            posts = self.repository.get_latest_posts(limit=100)
            
        return posts
    
    def get_post(self, post_id):
        """Get a specific post by ID"""
        return self.repository.get_post_by_id(post_id)
    
    def get_categories(self):
        """Get all forum categories"""
        return ParentsForum_Model.CATEGORY_CHOICES
    
    def get_category_counts(self):
        """Get counts of posts for each category"""
        counts = {}
        categories = ParentsForum_Model.objects.values('category').annotate(count=Count('id'))
        
        for item in categories:
            counts[item['category']] = item['count']
            
        return counts
    
    # Post manipulation methods
    def create_post(self, user, title, desc, category):
        """Create a new forum post"""
        post = ParentsForum_Model.objects.create(
            author=user,
            title=title,
            desc=desc,
            category=category
        )
        return post
    
    def update_post(self, post_id, title, desc, category):
        """Update an existing forum post"""
        post = self.get_post(post_id)
        post.title = title
        post.desc = desc
        post.category = category
        post.save()
        return post
    
    def delete_post(self, post_id):
        """Delete a forum post"""
        post = self.get_post(post_id)
        post.delete()
    
    # Interaction methods
    def toggle_like(self, post_id, user):
        """Toggle like for a post"""
        post = self.get_post(post_id)
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return False  # Unliked
        else:
            post.likes.add(user)
            return True  # Liked
    
    # Comment methods
    def get_post_comments(self, post_id):
        """Get comments for a post"""
        post = self.get_post(post_id)
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=post_id
        ).select_related('author').order_by('-created_at')
    
    def add_comment(self, post_id, user, text):
        """Add a comment to a post"""
        post = self.get_post(post_id)
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=post_id,
            author=user,
            text=text
        )
        
        return comment
    

    