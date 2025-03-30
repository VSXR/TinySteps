from django.db import models
from django.utils.translation import gettext_lazy as _

class Category_Model(models.Model):
    """Model for categories of content"""
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name=_("Parent Category")
    )
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_name(self):
        """Get the full hierarchical name of this category"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name