from django.urls import path

class ForumService_Factory:
    @staticmethod
    def create_service():
        """Create a forum service instance"""
        from tinySteps.services.core.forum_service import Forum_Service
        return Forum_Service()

class ForumUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for forum-related views"""
        from tinySteps.views.forum import forum_views
        
        return [
            path('forum/', forum_views.parents_forum_page, name='forum_home'),
            path('forum/post/<int:post_id>/', forum_views.view_post, name='view_post'),
            path('forum/post/create/', forum_views.add_post, name='create_post'),
            path('forum/post/<int:post_id>/edit/', forum_views.edit_post, name='edit_post'),
            path('forum/post/<int:post_id>/delete/', forum_views.delete_post, name='delete_post'),
        ]