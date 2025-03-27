from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext as _

class Comment_Model(models.Model):
    """Comment model"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='all_comments')
    text = models.TextField(_("Text"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
    
    def __str__(self):
        truncated_text = (self.text[:30] + "...") if len(self.text) > 30 else self.text
        return f"{self.content_object} - {truncated_text}"

class Like_Model(models.Model):
    """Like model"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
    
    def __str__(self):
        return _("%(username)s liked %(object)s") % {'username': self.user.username, 'object': self.content_object}