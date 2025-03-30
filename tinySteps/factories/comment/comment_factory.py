from django.urls import path, include

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
        from tinySteps.views.comments import urls
        return urls.urlpatterns