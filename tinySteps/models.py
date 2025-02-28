from django.db import models
from django.urls import reverse

# INFO REQUEST MODEL
class InfoRequestModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    
    def __str__(self):
        return f"{self.name}, your info request has been submitted correctly!"
    
    def get_absolute_url(self):
        return reverse('info_request')

# CHILD MODEL (FOR CHILDREN PAGE: YOUR CHILDREN VIEWED IN CARDS)
class ChildModel(models.Model):
    name = models.CharField(unique=True, null=False, blank=False, max_length=50)
    image_url = models.URLField(max_length=200, null=False, blank=False)
    age = models.IntegerField(null=False, blank=False)
    desc = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('child_detail', kwargs={'pk': self.pk})
    
# FORUM MODEL
class ForumModel(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, null=False, blank=False)
    desc = models.TextField(max_length=2000, null=False, blank=False)
    comment = models.TextField()

    def __str__(self):
        truncated_comment = (self.comment[:30] + "...") if len(self.comment) > 30 else self.comment
        return f"{self.title} - {truncated_comment}"

# GUIDES MODEL
class GuideModel(models.Model):
    title = models.CharField(max_length=100)
    img_url = models.URLField(max_length=200, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    desc = models.TextField(max_length=2000, null=False, blank=False)    

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('guide_detail', kwargs={'pk': self.pk})