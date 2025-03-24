from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from ..models import ParentsForum_Model, Comment_Model, Like_Model
from ..repositories import Forum_Repository

class Forum_Service:
    """Service for forum operations implementing SRP and DIP"""
    
    def __init__(self, repository=None):
        self.repository = repository or Forum_Repository()
    
    def get_posts(self, page=1, search=None, category=None, per_page=10):
        """Get forum posts with optional filtering"""
        posts = self.repository.get_posts(search, category)
        
        # Return the posts directly (pagination handled in view)
        return posts
    
    def get_post(self, post_id):
        """Get a specific post by ID"""
        return self.repository.get_post_by_id(post_id)
    
    def get_post_comments(self, post_id):
        """Get comments for a post"""
        post = self.get_post(post_id)
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=post_id
        ).select_related('author').order_by('-created_at')
    
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
    
    def toggle_like(self, post_id, user):
        """Toggle like for a post"""
        post = self.get_post(post_id)
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            return False  # Unliked
        else:
            post.likes.add(user)
            return True  # Liked
    
    def get_related_posts(self, post_id, limit=3):
        """Get related posts by category"""
        post = self.get_post(post_id)
        return ParentsForum_Model.objects.filter(
            category=post.category
        ).exclude(id=post_id).order_by('-created_at')[:limit]
    
    def get_post_stats(self, post_id):
        """Get statistics for a post"""
        post = self.get_post(post_id)
        return {
            'likes': post.likes.count(),
            'comments': post.comments.count()
        }