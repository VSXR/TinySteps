from django.db import models
from django.utils.translation import gettext as _

class ExternalArticle_Model(models.Model):
    """External article model"""
    title = models.CharField(_("Title"), max_length=255)
    source_name = models.CharField(_("Source Name"), max_length=100)
    author = models.CharField(_("Author"), max_length=100, null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    url = models.URLField(_("URL"))
    image_url = models.URLField(_("Image URL"), null=True, blank=True)
    published_at = models.DateTimeField(_("Published At"))
    category = models.CharField(_("Category"), max_length=50, choices=[
        ('parenting', _('Parenting')),
        ('nutrition', _('Nutrition'))
    ])
    content = models.TextField(_("Content"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("External Article")
        verbose_name_plural = _("External Articles")
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title