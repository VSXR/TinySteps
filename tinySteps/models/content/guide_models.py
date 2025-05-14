import time
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.utils import timezone
from django.templatetags.static import static

from tinySteps.models.base.mixins import CommentableMixin
from tinySteps.models.content.category_models import Category_Model
from tinySteps.models.external.article_models import ExternalArticle_Model


class Guide_Interface(models.Model):
    """Abstract base class for all guide models"""
    
    class Meta:
        abstract = True
    
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


class BaseGuide_Manager(models.Manager):
    """Base manager for guide models"""
    def get_approved(self):
        return self.filter(status='approved')

    def get_pending(self):
        return self.filter(status='pending')
    
    def get_rejected(self):
        return self.filter(status='rejected')


class ParentGuides_Manager(BaseGuide_Manager):
    """Manager for parent guides"""
    def get_queryset(self):
        return super().get_queryset().filter(guide_type='parent')


class NutritionGuides_Manager(BaseGuide_Manager):
    """Manager for nutrition guides"""
    def get_queryset(self):
        return super().get_queryset().filter(guide_type='nutrition')


class Guides_Model(Guide_Interface, CommentableMixin):
    """Base model for guides with shared fields and functionality"""
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
    
    # Basic fields
    title = models.CharField(max_length=100, validators=[MinLengthValidator(5)])
    desc = models.TextField(max_length=2000, validators=[MinLengthValidator(300)])
    slug = models.SlugField(
        _("Slug"),
        unique=True,
        blank=True,
        help_text=_("SEO-friendly URL; auto-generated if empty.")
    )
    summary = models.CharField(_("Summary"), max_length=200, blank=True, null=True)
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

    # Optional fields
    # These fields are optional and can be set to null or blank if we want
    summary = models.CharField(_("Summary"), max_length=200, blank=True, null=True)

    # Classification and status
    guide_type = models.CharField(_("Guide type"), max_length=20, choices=GUIDE_TYPE_CHOICES, default='parent')
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    published_at = models.DateTimeField(_("Published at"), null=True, blank=True)
    approved_at = models.DateTimeField(_("Approved at"), null=True, blank=True)
    
    # Relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guides')
    comments = GenericRelation('Comment_Model', related_query_name='guide')
    category = models.ForeignKey(
        Category_Model, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='%(class)s',
        verbose_name=_("Category")
    )
    
    # Moderation data
    rejection_reason = models.TextField(_("Rejection Reason"), max_length=500, null=True, blank=True)
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='moderated_guides'
    )
    moderation_notes = models.TextField(_("Moderation Notes"), max_length=500, null=True, blank=True)
    moderation_date = models.DateTimeField(_("Moderation Date"), null=True, blank=True)

    # Default manager
    objects = models.Manager()
    
    class Meta:
        verbose_name = _("Guide")
        verbose_name_plural = _("Guides")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['guide_type']),
            models.Index(fields=['author']),
        ]
        permissions = [
            ("can_moderate_guide", "Can moderate guides"),
        ]

    # Properties
    @property
    def is_approved(self):
        return self.status == 'approved'
        
    @property
    def is_pending(self):
        return self.status == 'pending'
        
    @property
    def is_rejected(self):
        return self.status == 'rejected'
    
    # Methods
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = f"{slugify(self.title)}-{int(time.time())}"
            
        # Set published_at when approved
        if self.status == 'approved' and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(f'{self.guide_type}_guide_details', kwargs={'pk': self.pk})
    
    def get_image_url(self):
        """Return the image URL or a default image if not available"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return static('res/img/others/default.jpg')
    @property
    def predefined_tags(self):
        return self.PREDEFINED_TAGS.get(self.guide_type, [])
        
    def set_tags(self, tags):
        """Set tags for the guide as a comma-separated string"""
        if isinstance(tags, list):
            self.tags = ','.join(tags)
        else:
            self.tags = tags
        self.save(update_fields=['tags'])
    
    @classmethod
    def create_from_form(cls, form, guide_type, user):
        """Create a new guide from a form"""
        import time
        
        guide = cls(
            title=form.cleaned_data['title'],
            desc=form.cleaned_data['desc'],
            summary=form.cleaned_data.get('summary', ''),
            image=form.cleaned_data.get('image'),
            author=user,
            guide_type=guide_type,
            slug=f"{slugify(form.cleaned_data['title'])}-{int(time.time())}"
        )
        
        if form.cleaned_data.get('category'):
            guide.category = form.cleaned_data.get('category')
            
        guide.save()
        
        # Handle tags from the form
        tags_text = form.cleaned_data.get('tags', '')
        if tags_text:
            guide.set_tags(tags_text)
            
        return guide


class ParentsGuides_Model(Guides_Model):
    """Model for parent-specific guides"""
    objects = ParentGuides_Manager()
    
    class Meta:
        proxy = True
        verbose_name = _("Parent Guide")
        verbose_name_plural = _("Parent Guides")
    
    def save(self, *args, **kwargs):
        self.guide_type = 'parent'
        super().save(*args, **kwargs)
    
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
        ).order_by('-published_at')[:5]


class NutritionGuides_Model(Guides_Model):
    """Model for nutrition-specific guides"""
    objects = NutritionGuides_Manager()
    
    class Meta:
        proxy = True
        verbose_name = _("Nutrition Guide")
        verbose_name_plural = _("Nutrition Guides")
    
    def save(self, *args, **kwargs):
        self.guide_type = 'nutrition'
        super().save(*args, **kwargs)
    
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
        ).order_by('-published_at')[:5]