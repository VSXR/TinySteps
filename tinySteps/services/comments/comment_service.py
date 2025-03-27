from django.contrib.contenttypes.models import ContentType
from tinySteps.repositories.content.comment_repository import Comment_Repository

class Comment_Service:
    def __init__(self):
        self.repository = Comment_Repository()
    
    def add_comment(self, content_type_str, object_id, content, user):
        """Add a comment to a content object"""
        content_type_mapping = {
            'parent_guide': 'guides_model',
            'nutrition_guide': 'guides_model',
            'forum_post': 'forumpost_model',
        }
        
        if content_type_str not in content_type_mapping:
            raise ValueError(f"Unsupported content type: {content_type_str}")
            
        model = content_type_mapping[content_type_str]
        
        # Obtener ContentType para saber a qué modelo se refiere
        content_type = ContentType.objects.get(
            app_label='tinySteps',
            model=model
        )
        
        # Crear el comentario
        return self.repository.create_comment(
            content_type=content_type,
            object_id=object_id,
            text=content,
            author=user
        )
    
    def get_comments(self, content_type_str, object_id):
        """Get comments for a content object"""
        content_type_mapping = {
            'parent_guide': 'guides_model',
            'nutrition_guide': 'guides_model',
            'forum_post': 'forumpost_model',
        }
        
        if content_type_str not in content_type_mapping:
            raise ValueError(f"Unsupported content type: {content_type_str}")
            
        model = content_type_mapping[content_type_str]
        content_type = ContentType.objects.get(
            app_label='tinySteps',
            model=model
        )
        
        return self.repository.get_comments_for_object(content_type, object_id)
    
    def delete_comment(self, comment_id, user):
        """Delete a comment if user is author or admin"""
        comment = self.repository.get_by_id(comment_id)
        
        if not comment:
            return False
            
        # Verificar si el usuario es el autor o administrador
        if comment.author == user or user.is_staff:
            self.repository.delete(comment)
            return True
            
        return False