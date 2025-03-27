from django.db import models
from django.utils.translation import gettext as _

class ExternalNutritionData_Model(models.Model):
    """External nutrition data model for ingredients"""
    ingredient = models.CharField(_("Ingredient"), max_length=200)
    data = models.JSONField(_("Nutrition Data"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("External Nutrition Data")
        verbose_name_plural = _("External Nutrition Data")
        unique_together = ('ingredient',)
    
    def __str__(self):
        return f"Nutrition data for {self.ingredient}"