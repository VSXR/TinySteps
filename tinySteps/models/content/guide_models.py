import time
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.text import slugify

from tinySteps.models.base.mixins import CommentableMixin
from tinySteps.models.external.article_models import ExternalArticle_Model

class Guide_Interface(models.Model):
    """Abstract base class for the Guide interface class"""
    
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
        """Create a new guide from a form"""
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
    Base manager for guide models
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
    """Proxy model for nutrition guides"""
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
        ).order_by('-published_at')[:3]