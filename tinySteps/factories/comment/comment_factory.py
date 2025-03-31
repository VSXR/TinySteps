from django.urls import path

class CommentService_Factory:
    @staticmethod
    def create_service():
        """Create a comment service instance"""
        from tinySteps.services.comments.comment_service import Comment_Service
        return Comment_Service()

class CommentUrl_Factory:
    @staticmethod
    def create_urls():
        """Create URL patterns for the comments section"""
        from tinySteps.views.comments import comment_views
        
        urlpatterns = [
            path('add/<str:content_type>/<int:object_id>/', comment_views.add_comment, name='add_comment'),
            path('delete/<int:comment_id>/', comment_views.delete_comment, name='delete_comment'),
            path('list/<str:content_type>/<int:object_id>/', comment_views.list_comments, name='list_comments'),
        ]
        
        return urlpatterns