from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

class Notification_Model(models.Model):
    """Notification model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    read = models.BooleanField(_("Read"), default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        
    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}..."