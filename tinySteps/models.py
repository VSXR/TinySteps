import uuid, time
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from .services import NewsAPIService, CurrentsAPI

# ------------------------------------------
# -- GENERIC MODELS --
# ------------------------------------------
class Comment_Model(models.Model):
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

class Notification_Model(models.Model):
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

# ------------------------------------------
# -- USER RELATED MODELS --
# ------------------------------------------
# TODO: USER PROFILE MODEL

class PasswordReset_Model(models.Model):
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

# ------------------------------------------
# -- CHILD RELATED MODELS --
# ------------------------------------------
class YourChild_Model(models.Model):
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
        return reverse('child_details', kwargs={'pk': self.pk})
    
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
    child = models.ForeignKey(YourChild_Model, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(_("Title"), max_length=100)
    achieved_date = models.DateField(_("Achieved date"))
    description = models.TextField(_("Description"))
    photo = models.ImageField(_("Photo"), upload_to='milestone_photos/', blank=True, null=True)
    
    class Meta:
        verbose_name = _("Milestone")
        verbose_name_plural = _("Milestones")

class VaccineCard_Model(models.Model):
    child = models.OneToOneField(YourChild_Model, on_delete=models.CASCADE, related_name='vaccine_card')
    vaccines = GenericRelation('Vaccine_Model', related_query_name='vaccine_card')
    
    class Meta:
        verbose_name = _("Vaccine Card")
        verbose_name_plural = _("Vaccine Cards")
    
    def __str__(self):
        return _("Vaccine card for %(name)s") % {'name': self.child.name}
    
    def get_absolute_url(self):
        return reverse('vaccine_card', kwargs={'pk': self.child.pk})
    
class Vaccine_Model(models.Model):
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
    TYPE_CHOICES = (
        ('doctor', _("Medical Appointment")),
        ('vaccine', _("Vaccine")),
        ('milestone', _("Development Milestone")),
        ('feeding', _("Feeding")),
        ('other', _("Other")),
    )
    
    child = models.ForeignKey(YourChild_Model, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(_("Title"), max_length=255)
    type = models.CharField(_("Type"), max_length=20, choices=TYPE_CHOICES, default='other')
    date = models.DateField(_("Date"))
    time = models.TimeField(_("Time"), null=True, blank=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    has_reminder = models.BooleanField(_("Has reminder"), default=False)
    reminder_minutes = models.IntegerField(_("Reminder minutes"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    
    class Meta:
        verbose_name = _("Calendar Event")
        verbose_name_plural = _("Calendar Events")
    
    def get_event_color(self):
        color_map = {
            'doctor': '#4285F4',
            'vaccine': '#EA4335',
            'milestone': '#FBBC05',
            'feeding': '#34A853',
            'other': '#8f6ed5',
        }
        return color_map.get(self.type, '#8f6ed5')
    
    def __str__(self):
        return f"{self.title} - {self.date}"

# ------------------------------------------
# -- CONTENT MODELS --
# ------------------------------------------
class ParentsForum_Model(models.Model):
    title = models.CharField(_("Title"), max_length=100, db_index=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    desc = models.TextField(_("Description"), max_length=2000, null=False, blank=False)
    comments = GenericRelation(Comment_Model, related_query_name='forum')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'title']),
        ]
        verbose_name = _("Parents Forum Post")
        verbose_name_plural = _("Parents Forum Posts")
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    def __str__(self):
        truncated_desc = (self.desc[:30] + "...") if len(self.desc) > 30 else self.desc
        return f"{self.title} - {truncated_desc}"

    def get_absolute_url(self):
        return reverse('view_post', kwargs={'post_id': self.pk})

class Guides_Model(models.Model):
    GUIDE_TYPE_CHOICES = (
        ('parent', _("Parent Guide")),
        ('nutrition', _("Nutrition Guide")),
    )
    
    title = models.CharField(_("Title"), max_length=100)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    author = models.CharField(_("Author"), max_length=100, null=False, blank=False)
    desc = models.TextField(_("Description"), max_length=2000, null=False, blank=False)
    image_url = models.CharField(_("Image URL"), max_length=200, default='images/others/default.jpg')
    guide_type = models.CharField(_("Guide type"), max_length=20, choices=GUIDE_TYPE_CHOICES, default='parent')
    comments = GenericRelation(Comment_Model, related_query_name='guide')
    
    class Meta:
        verbose_name = _("Guide")
        verbose_name_plural = _("Guides")
    
    def __str__(self):
        truncated_desc = (self.desc[:30] + "...") if len(self.desc) > 30 else self.desc
        return f"{self.title} - {truncated_desc}"
    
    def get_absolute_url(self):
        if self.guide_type == 'parent':
            return reverse('parents_guide_details', kwargs={'pk': self.pk})
        elif self.guide_type == 'nutrition':
            return reverse('nutrition_guide_details', kwargs={'pk': self.pk})
        return reverse('guide_details', kwargs={'pk': self.pk})

class ParentsGuides_Model(Guides_Model):
    class Meta:
        proxy = True
        verbose_name = _("Parent Guide")
        verbose_name_plural = _("Parent Guides")
        
    def save(self, *args, **kwargs):
        self.guide_type = 'parent'
        super().save(*args, **kwargs)
    
    @classmethod
    def get_queryset(cls):
        return Guides_Model.objects.filter(guide_type='parent')
        
class NutritionGuides_Model(Guides_Model):
    class Meta:
        proxy = True
        verbose_name = _("Nutrition Guide")
        verbose_name_plural = _("Nutrition Guides")
        
    def save(self, *args, **kwargs):
        self.guide_type = 'nutrition'
        super().save(*args, **kwargs)
    
    @classmethod
    def get_queryset(cls):
        return Guides_Model.objects.filter(guide_type='nutrition')

# ------------------------------------------
# -- UTILITY MODELS --
# ------------------------------------------
class Contact_Model(models.Model):
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
    
# ------------------------------------------
# -- EXTERNAL APIs MODELS --
# ------------------------------------------
class ExternalArticle_Model(models.Model):
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
    
    @classmethod
    def update_from_apis(cls, topic=None):
        news_service = NewsAPIService()
        currents_service = CurrentsAPI()
        
        if topic:
            articles = news_service.get_parenting_articles_by_topic(topic, force_refresh=True)
            news = currents_service.get_news_by_topic(topic, force_refresh=True)
        else:
            articles = news_service.get_parenting_articles(force_refresh=True)
            news = currents_service.get_first_time_parent_news(force_refresh=True)
        
        if articles:
            cls._update_articles(articles)

        if news:
            cls._update_news(news)
        
        return True

class ExternalNutritionData_Model(models.Model):
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