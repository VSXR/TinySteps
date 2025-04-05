import time
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _


class YourChild_Model(models.Model):
    """Model for children"""
    GENDER_CHOICES = [
        ('M', _("Male")),
        ('F', _("Female")),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    
    name = models.CharField(_("Name"), unique=True, null=False, blank=False, max_length=50)
    second_name = models.CharField(_("Second name"), max_length=50, null=True, blank=True)
    
    birth_date = models.DateField(_("Birth date"), null=False, blank=False)
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES, null=False, blank=False)
    age = models.IntegerField(_("Age"), null=False, blank=False)
    
    weight = models.FloatField(_("Weight"), null=True, blank=True)
    height = models.FloatField(_("Height"), null=True, blank=True)
    
    desc = models.TextField(_("Description"), max_length=2000, null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to='child_photos/', null=True, blank=True)
    image_url = models.URLField(_("Image URL"), max_length=200, null=True, blank=True) 
    
    class Meta:
        verbose_name = _("Child")
        verbose_name_plural = _("Children")
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('child_detail', kwargs={'pk': self.pk})
    
    @property
    def get_image(self):
        cache_buster = f"?v={int(time.time())}"
        
        if self.image and hasattr(self.image, 'url'):
            return f"{self.image.url}{cache_buster}"
        elif self.image_url:
            return f"{self.image_url}{cache_buster}"
        else:
            return f"/static/res/img/others/default_child.jpg{cache_buster}"

class Milestone_Model(models.Model):
    """Model for milestones"""
    child = models.ForeignKey(YourChild_Model, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(_("Title"), max_length=100)
    achieved_date = models.DateField(_("Achieved date"))
    description = models.TextField(_("Description"))
    photo = models.ImageField(_("Photo"), upload_to='milestone_photos/', blank=True, null=True)
    
    class Meta:
        verbose_name = _("Milestone")
        verbose_name_plural = _("Milestones")

class VaccineCard_Model(models.Model):
    """Model for vaccine cards"""
    child = models.OneToOneField(YourChild_Model, on_delete=models.CASCADE, related_name='vaccine_card')
    
    class Meta:
        verbose_name = _("Vaccine Card")
        verbose_name_plural = _("Vaccine Cards")
    
    def __str__(self):
        return _("Vaccine card for %(name)s") % {'name': self.child.name}
    
    def get_absolute_url(self):
        return reverse('vaccine_card', kwargs={'pk': self.child.pk})
    
class Vaccine_Model(models.Model):
    """Model for vaccines"""
    vaccine_card = models.ForeignKey(VaccineCard_Model, on_delete=models.CASCADE, related_name='vaccines')
    name = models.CharField(_("Name"), max_length=100)
    date = models.DateField(_("Date"))
    notes = models.TextField(_("Notes"), null=True, blank=True)
    administered = models.BooleanField(_("Administered"), default=False)
    next_dose_date = models.DateField(_("Next dose date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Vaccine")
        verbose_name_plural = _("Vaccines")

    def __str__(self):
        return f"{self.name} - {self.date}"





class CalendarEvent_Model(models.Model):
    """Model for child calendar events"""
    
    TYPE_CHOICES = [
        ('doctor', _("Doctor Appointment")),
        ('vaccine', _("Vaccine")),
        ('milestone', _("Development Milestone")),
        ('feeding', _("Feeding")),
        ('other', _("Other")),
    ]
    
    STATUS_CHOICES = [
        ('pending', _("Pending")),
        ('completed', _("Completed")),
        ('cancelled', _("Cancelled")),
    ]
    
    child = models.ForeignKey(YourChild_Model, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_("Type"))

    # Date and time information
    date = models.DateField(verbose_name=_("Date"))
    time = models.TimeField(null=True, blank=True, verbose_name=_("Time"))
    is_all_day = models.BooleanField(default=False, verbose_name=_("All day event"))
    
    # Event details
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Location"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    
    # Event status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))
    
    # Reminder settings
    has_reminder = models.BooleanField(default=False, verbose_name=_("Has reminder"))
    reminder_minutes = models.IntegerField(null=True, blank=True, verbose_name=_("Reminder minutes"))
    reminder_sent = models.BooleanField(default=False, verbose_name=_("Reminder sent"))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        ordering = ["date", "time"]
        verbose_name = _("Calendar Event")
        verbose_name_plural = _("Calendar Events")
        indexes = [
            models.Index(fields=['child', 'date']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.date}"
        
    def is_upcoming(self):
        """Check if the event is in the future"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.date >= today
        
    def get_absolute_url(self):
        """Get the URL for this event"""
        return reverse('children:event_detail', kwargs={'child_id': self.child.id, 'event_id': self.pk})