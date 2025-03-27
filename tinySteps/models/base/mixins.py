class CommentableMixin:
    """Mixin class for models that can receive comments"""
    
    @property
    def comments_count(self):
        """Get the number of comments for this object"""
        from django.contrib.contenttypes.models import ContentType
        from tinySteps.models.content.comment_models import Comment_Model
        
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).count()
    
    def add_comment(self, user, text):
        """Add a comment to this object"""
        from django.contrib.contenttypes.models import ContentType
        from tinySteps.models.content.comment_models import Comment_Model
        
        content_type = ContentType.objects.get_for_model(self.__class__)
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=self.id,
            author=user,
            text=text
        )
        return comment

class LikeableMixin:
    """Mixin for models that can be liked"""
    
    @property
    def likes_count(self):
        """Get the number of likes for this object"""
        from django.contrib.contenttypes.models import ContentType
        from tinySteps.models.content.comment_models import Like_Model
        
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Like_Model.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).count()
    
    def toggle_like(self, user):
        """Toggle like status for this object"""
        from django.contrib.contenttypes.models import ContentType
        from tinySteps.models.content.comment_models import Like_Model
        
        content_type = ContentType.objects.get_for_model(self.__class__)
        like, created = Like_Model.objects.get_or_create(
            content_type=content_type,
            object_id=self.id,
            user=user
        )
        if not created:
            like.delete()
            return False
        return True