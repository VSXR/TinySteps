import uuid
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone


# ------------------------------------------
# -- GENERIC COMMENT MODEL --
# ------------------------------------------
class Comment_Model(models.Model):
    # CAMPOS GENERICOS DE COMENTARIOS ENTRE FOROS Y GUIAS
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # CAMPOS ESPECIFICOS DE LOS COMENTARIOS ENTRE FOROS Y GUIAS
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='all_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        truncated_text = (self.text[:30] + "...") if len(self.text) > 30 else self.text
        return f"{self.content_object} - {truncated_text}"
# ------------------------------------------

# ------------------------------------------
# -- GENERIC LIKE MODEL --
# ------------------------------------------
class Like_Model(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'user')
        verbose_name = "Like"
        verbose_name_plural = "Likes"
    
    def __str__(self):
        return f"{self.user.username} liked {self.content_object}"
# ------------------------------------------

# ------------------------------------------
# -- NOTIFICATION MODELS --
# ------------------------------------------
class Notification_Model(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}..."
# ------------------------------------------

# ------------------------------------------
# -- TODO: USER PROFILE MODEL --
# ------------------------------------------


# ------------------------------------------
# -- PASSWORD RESET MODEL --
# ------------------------------------------
class PasswordReset_Model(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
    @property
    def is_expired(self):
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiry_time
    
    def get_absolute_url(self):
        return reverse('password_reset_confirm', kwargs={'token': self.token})
# ------------------------------------------

# ------------------------------------------
# -- CHILD MODELS --
# ------------------------------------------
class YourChild_Model(models.Model):
    name = models.CharField(unique=True, null=False, blank=False, max_length=50)
    second_name = models.CharField(max_length=50, null=True, blank=True)
    birth_date = models.DateField(null=False, blank=False)
    image_url = models.URLField(max_length=200, null=False, blank=False)
    age = models.IntegerField(null=False, blank=False)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=1, null=False, blank=False)
    desc = models.TextField(max_length=2000, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('child_details', kwargs={'pk': self.pk})

class Milestone_Model(models.Model):
    child = models.ForeignKey(YourChild_Model, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=100)
    achieved_date = models.DateField()
    description = models.TextField()
    photo = models.ImageField(upload_to='milestone_photos/', blank=True, null=True)
# ------------------------------------------

# ------------------------------------------
# -- PARENTS FORUM MODELS --
# ------------------------------------------
class ParentsForum_Model(models.Model):
    title = models.CharField(max_length=100, db_index=True)  # Add index for search
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index for sorting
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    desc = models.TextField(max_length=2000, null=False, blank=False)
    comments = GenericRelation(Comment_Model, related_query_name='forum')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'title']),
        ]
    
    def __str__(self):
        truncated_desc = (self.desc[:30] + "...") if len(self.desc) > 30 else self.desc
        return f"{self.title} - {truncated_desc}"

    def get_absolute_url(self):
        return reverse('view_post', kwargs={'post_id': self.pk})
# ------------------------------------------

# ------------------------------------------
# -- GUIDES MODELS (USA HERENCIA) --
# ------------------------------------------
class Guides_Model(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, null=False, blank=False)
    desc = models.TextField(max_length=2000, null=False, blank=False)
    image_url = models.CharField(max_length=200, default='images/others/default.jpg')
    
    GUIDE_TYPE_CHOICES = (
        ('parent', 'Parent Guide'),
        ('nutrition', 'Nutrition Guide'),
    )
    guide_type = models.CharField(max_length=20, choices=GUIDE_TYPE_CHOICES, default='parent')
    
    comments = GenericRelation(Comment_Model, related_query_name='guide')
    
    def __str__(self):
        truncated_desc = (self.desc[:30] + "...") if len(self.desc) > 30 else self.desc
        return f"{self.title} - {truncated_desc}"
    
    def get_absolute_url(self):
        if self.guide_type == 'parent':
            return reverse('parents_guide_details', kwargs={'pk': self.pk})
        elif self.guide_type == 'nutrition':
            return reverse('nutrition_guide_details', kwargs={'pk': self.pk})
        return reverse('guide_details', kwargs={'pk': self.pk})

# MODELOS PROXY PARA FILTRAR LOS GUIDES POR TIPO
# ------------------------------------------
class ParentsGuides_Model(Guides_Model):
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        self.guide_type = 'parent'
        super().save(*args, **kwargs)
    
    @classmethod
    def get_queryset(cls):
        return Guides_Model.objects.filter(guide_type='parent')
        
class NutritionGuides_Model(Guides_Model):
    class Meta:
        proxy = True
        
    def save(self, *args, **kwargs):
        self.guide_type = 'nutrition'
        super().save(*args, **kwargs)
    
    @classmethod
    def get_queryset(cls):
        return Guides_Model.objects.filter(guide_type='nutrition')
# ------------------------------------------

# ------------------------------------------
# -- INFO REQUEST MODELS --
# ------------------------------------------
class InfoRequest_Model(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    
    def __str__(self):
        return f"{self.name}, your info request has been submitted correctly!"
    
    def get_absolute_url(self):
        return reverse('info_request')
# ------------------------------------------
