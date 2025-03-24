import uuid, time
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.text import slugify

# ------------------------------------------
# -- USER RELATED MODELS --
# ------------------------------------------
class Profile_Model(models.Model):
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


class CommentableMixin:
    """Mixin for models that can receive comments - supports DIP"""
    
    @property
    def comments_count(self):
        """Get the number of comments for this object"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).count()
    
    def add_comment(self, user, text):
        """Add a comment to this object"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(self.__class__)
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=self.id,
            author=user,
            text=text
        )
        return comment

class LikeableMixin:
    """Mixin for models that can be liked - supports DIP"""
    
    @property
    def likes_count(self):
        """Get the number of likes for this object"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Like_Model.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).count()
    
    def toggle_like(self, user):
        """Toggle like status for this object"""
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(self.__class__)
        like, created = Like_Model.objects.get_or_create(
            content_type=content_type,
            object_id=self.id,
            user=user
        )
        if not created:
            like.delete()
            return False
        return True



# ------------------------------------------
# -- GUIDES MODELS --
# ------------------------------------------
class Guide_Interface(models.Model):
    """Abstract base class for the Guide interface class following ISP"""
    
    class Meta:
        abstract = True  # ABSTRACT CLASS FOR GUIDES!
    
    def get_related_content(self):
        """Get content related to this guide"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @classmethod
    def get_latest(cls, count=5):
        """Get latest guides of this type"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @classmethod
    def get_related_articles(cls):
        """Get related external articles for this guide type"""
        raise NotImplementedError("Subclasses must implement this method")
    
class Guides_Model(Guide_Interface, CommentableMixin):
    GUIDE_TYPE_CHOICES = (
        ('parent', _("Parent Guide")),
        ('nutrition', _("Nutrition Guide")),
    )
    STATUS_CHOICES = (
        ('pending', _("Pending Approval")),
        ('approved', _("Approved")),
        ('rejected', _("Rejected")),
    )
    PREDEFINED_TAGS = {
        'parent': ['parenting', 'childcare', 'education'],
        'nutrition': ['diet', 'health', 'recipes']
    }
    
    title = models.CharField(_("Title"), max_length=100)
    slug = models.SlugField(
        _("Slug"),
        unique=True,
        blank=True,
        help_text=_("SEO-friendly URL; auto-generated if empty.")
    )
    desc = models.TextField(_("Description"), max_length=2000)
    image = models.ImageField(
        _("Image"),
        upload_to='guide_images/',
        null=True,
        blank=True,
        help_text=_("Upload an image for the guide.")
    )
    tags = models.TextField(
        _("Tags"),
        null=True,
        blank=True,
        help_text=_("Comma-separated tags for the guide.")
    )
    guide_type = models.CharField(_("Guide type"), max_length=20, choices=GUIDE_TYPE_CHOICES, default='parent')
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    published_at = models.DateTimeField(
        _("Published at"), null=True, blank=True,
        help_text=_("Set this field when the guide is published.")
    )
    approved_at = models.DateTimeField(_("Approved at"), null=True, blank=True)
    rejection_reason = models.TextField(_("Rejection Reason"), max_length=500, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guides')
    comments = GenericRelation('Comment_Model', related_query_name='guide')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(f'{self.guide_type}_guide_details', kwargs={'pk': self.pk})
        
    @property
    def predefined_tags(self):
        return self.PREDEFINED_TAGS.get(self.guide_type, [])
    
    def set_tags(self, tags):
        """Set tags for the guide as a comma-separated string!"""
        if isinstance(tags, list):
            self.tags = ','.join([tag.strip() for tag in tags if tag.strip()])
        elif isinstance(tags, str):
            self.tags = ','.join([tag.strip() for tag in tags.split(',') if tag.strip()])
        else:
            self.tags = None
        self.save()

    @classmethod
    def create_from_form(cls, form, guide_type, user):
        """ Create a new guide from a form """
        guide = cls(
            title=form.cleaned_data['title'],
            desc=form.cleaned_data['desc'],
            image=form.cleaned_data.get('image'),
            author=user,
            guide_type=guide_type,
            slug=f"{slugify(form.cleaned_data['title'])}-{int(time.time())}"
        )
        
        guide.save()
        
        # Handle tags from the form
        tags_text = form.cleaned_data.get('tags', '')
        if tags_text:
            guide.set_tags(tags_text)
            
        return guide

class BaseGuide_Manager(models.Manager):
    """
    Base manager for guide models implementing the Liskov Substitution Principle
    This manager provides common functionality for managing guide objects,
    such as filtering approved guides. It serves as a foundation for more
    specific guide managers like ParentGuides_Manager and NutritionGuides_Manager
    """

    def get_approved(self):
        return self.filter(status='approved')

class ParentGuides_Manager(BaseGuide_Manager):
    """Manager for parent guides"""
    def get_queryset(self):
        return super().get_queryset().filter(guide_type='parent')

class ParentsGuides_Model(Guides_Model):
    objects = ParentGuides_Manager()
    
    class Meta:
        proxy = True
        verbose_name = _("Parent Guide")
        verbose_name_plural = _("Parent Guides")
    
    def save(self, *args, **kwargs):
        self.guide_type = 'parent'
        super().save(*args, **kwargs)
    
    # USES THE EXTERNAL ARTICLES DATA!
    def get_related_content(self):
        """Get content related to this guide"""
        return {
            'guides': ParentsGuides_Model.objects.filter(
                status='approved'
            ).exclude(pk=self.pk)[:3],
            'articles': ExternalArticle_Model.objects.filter(
                category='parenting'
            ).order_by('-published_at')[:3]
        }

    @classmethod
    def get_latest(cls, count=5):
        """Get latest parent guides"""
        return cls.objects.filter(
            guide_type='parent',
            status='approved'
        ).order_by('-created_at')[:count]
    
    @classmethod
    def get_related_articles(cls):
        """Get related external articles for parent guides"""
        return ExternalArticle_Model.objects.filter(
            category='parenting'
        ).order_by('-published_at')[:3]

class NutritionGuides_Manager(BaseGuide_Manager):
    """Manager for nutrition guides"""
    def get_queryset(self):
        return super().get_queryset().filter(guide_type='nutrition')
      
class NutritionGuides_Model(Guides_Model):
    """Proxy model for nutrition guides implementing the Interface Segregation Principle"""
    objects = NutritionGuides_Manager()
    
    class Meta:
        proxy = True
        verbose_name = _("Nutrition Guide")
        verbose_name_plural = _("Nutrition Guides")
    
    def save(self, *args, **kwargs):
        self.guide_type = 'nutrition'
        super().save(*args, **kwargs)

    # USES THE EXTERNAL NUTRITION DATA!
    def get_related_content(self):
        """Get content related to this guide"""
        return {
            'guides': NutritionGuides_Model.objects.filter(
                status='approved'
            ).exclude(pk=self.pk)[:3],
            'articles': ExternalArticle_Model.objects.filter(
                category='nutrition'
            ).order_by('-published_at')[:3]
        }
    
    @classmethod
    def get_latest(cls, count=5):
        """Get latest nutrition guides"""
        return cls.objects.filter(
            guide_type='nutrition',
            status='approved'
        ).order_by('-created_at')[:count]
    
    @classmethod
    def get_related_articles(cls):
        """Get related external articles for nutrition guides"""
        return ExternalArticle_Model.objects.filter(
            category='nutrition'
        ).order_by('-published_at')[:3]
    
    
# ------------------------------------------
# -- FORUM MODELS --
# ------------------------------------------
class ParentsForum_Model(models.Model, CommentableMixin, LikeableMixin):
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
        return reverse('view_post', kwargs={'post_id': self.pk})


# ------------------------------------------
# -- NOTIFICATION MODEL --
# ------------------------------------------
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
# -- CONTACT MODEL --
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
# -- LOGGING MODEL (FOR ADMIN) --
# ------------------------------------------
class ConnectionError_Model(models.Model):
    error_type = models.CharField(max_length=100)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    client_ip = models.GenericIPAddressField(null=True)
    user = models.CharField(max_length=150, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    traceback = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Connection Error"
        verbose_name_plural = "Connection Errors"
        
    def __str__(self):
        return f"{self.error_type} at {self.timestamp}"




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

