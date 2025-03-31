from django.urls import path, include

class ForumService_Factory:
    @staticmethod
    def create_service():
        """Create a forum service instance"""
        from tinySteps.services.core.forum_service import Forum_Service
        return Forum_Service()

class ForumUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for the parent forum section"""
        from tinySteps.views.forum import forum_views
        
        # Define URL patterns WITHOUT the forum/ prefix
        urlpatterns = [
            # Forum main views
            path('', forum_views.parents_forum_page, name='parent_forum'),
            
            # Post CRUD operations
            path('posts/create/', forum_views.add_post, name='create_post'),
            path('posts/<int:post_id>/', forum_views.view_post, name='view_post'),
            path('posts/<int:post_id>/edit/', forum_views.edit_post, name='edit_post'),
            path('posts/<int:post_id>/delete/', forum_views.delete_post, name='delete_post'),
            
            # Comment operations
            path('posts/<int:post_id>/comment/', forum_views.add_post_comment, name='add_post_comment'),
            
            # Like operations
            path('posts/<int:post_id>/like/', forum_views.forum_post_like_toggle, name='toggle_post_like'),
            
            # Category views
            path('categories/', forum_views.categories, name='forum_categories'),
        ]
        
        return urlpatterns