import uuid, time
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

class Profile_Model(models.Model):
    """User profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_("Bio"), max_length=2000, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to='profile_photos/', null=True, blank=True)
    image_url = models.URLField(_("Image URL"), max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
    
    def __str__(self):
        return self.user.username
    
    @property
    def get_image(self):
        cache_buster = f"?v={int(time.time())}"
        
        if self.image and hasattr(self.image, 'url'):
            return f"{self.image.url}{cache_buster}"
        elif self.image_url:
            return f"{self.image_url}{cache_buster}"
        else:
            return f"/static/res/img/others/default_profile.jpg{cache_buster}"

class PasswordReset_Model(models.Model):
    """Password reset token model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    is_used = models.BooleanField(_("Is used"), default=False)
    
    class Meta:
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")
    
    def __str__(self):
        return _("Password reset token for %(username)s") % {'username': self.user.username}
    
    @property
    def is_expired(self):
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiry_time
    
    def get_absolute_url(self):
        return reverse('password_reset_confirm', kwargs={'token': self.token})