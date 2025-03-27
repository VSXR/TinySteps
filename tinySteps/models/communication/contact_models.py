from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

class Contact_Model(models.Model):
    """Contact request model"""
    name = models.CharField(_("Name"), max_length=100)
    email = models.EmailField(_("Email"))
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Created at"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Contact Request")
        verbose_name_plural = _("Contact Requests")
    
    def __str__(self):
        return _("%(name)s, your info request has been submitted correctly!") % {'name': self.name}
    
    def get_absolute_url(self):
        return reverse('contact')