from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from tinySteps.models.base.mixins import CommentableMixin, LikeableMixin

class ParentsForum_Model(models.Model, CommentableMixin, LikeableMixin):
    """Model for Parents Forum posts"""
    CATEGORY_CHOICES = [
        ('advice', _('Advice')),
        ('feeding', _('Feeding')),
        ('sleep', _('Sleep')),
        ('health', _('Health')),
        ('development', _('Development')),
        ('care', _('Baby Care')),
    ]

    title = models.CharField(_("Title"), max_length=100, db_index=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    desc = models.TextField(_("Description"), max_length=2000, null=False, blank=False)
    category = models.CharField(
        _("Category"),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='advice'
    )
    comments = GenericRelation('Comment_Model', related_query_name='forum')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'title']),
        ]
        verbose_name = _("Parents Forum Post")
        verbose_name_plural = _("Parents Forum Posts")
    
    def __str__(self):
        truncated_desc = (self.desc[:30] + "...") if len(self.desc) > 30 else self.desc
        return f"{self.title} - {truncated_desc}"

    def get_absolute_url(self):
        return reverse('forum:view_post', kwargs={'post_id': self.pk})