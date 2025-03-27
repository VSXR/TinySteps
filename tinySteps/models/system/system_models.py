from django.db import models
from django.utils.translation import gettext_lazy as _

class ConnectionError_Model(models.Model):
    """Model for logging connection and request errors"""
    
    ERROR_TYPES = (
        ('broken_pipe', _('Broken Pipe')),
        ('connection_reset', _('Connection Reset')),
        ('timeout', _('Timeout')),
        ('internal_server', _('Internal Server Error')),
        ('other', _('Other Error'))
    )
    
    error_type = models.CharField(max_length=20, choices=ERROR_TYPES)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    client_ip = models.GenericIPAddressField(null=False, default='0.0.0.0')    
    user = models.CharField(max_length=150, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    traceback = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Connection Error')
        verbose_name_plural = _('Connection Errors')
    
    def __str__(self):
        return f"{self.error_type} at {self.path} ({self.timestamp})"