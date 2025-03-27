from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404

from tinySteps.models import Profile_Model
from tinySteps.repositories.base.base_repository import GenericRepository

class User_Repository(GenericRepository):
    """Repository for User model operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username):
        """Get a user by username"""
        return get_object_or_404(self.model, username=username)
    
    def get_by_email(self, email):
        """Get a user by email"""
        return get_object_or_404(self.model, email=email)
    
    def search_users(self, query):
        """Search users by username or email"""
        search_query = Q(username__icontains=query) | Q(email__icontains=query)
        return self.model.objects.filter(search_query)
    
    def get_active_users(self):
        """Get all active users"""
        return self.model.objects.filter(is_active=True)
    
    def get_staff_users(self):
        """Get all staff users"""
        return self.model.objects.filter(is_staff=True)
    
    def create_user(self, username, email, password, **extra_fields):
        """Create a new user"""
        user = self.model.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        return user
    
    def update_last_login(self, user):
        """Update the last login timestamp for a user"""
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return user


class Profile_Repository(GenericRepository):
    """Repository for Profile model operations"""
    
    def __init__(self):
        super().__init__(Profile_Model)
    
    def get_by_user(self, user):
        """Get a profile by user"""
        return get_object_or_404(self.model, user=user)
    
    def create_profile(self, user, **data):
        """Create a new profile for a user"""
        profile = self.model(user=user, **data)
        profile.save()
        return profile
    
    def update_profile(self, user, **data):
        """Update a user's profile"""
        profile = self.get_by_user(user)
        for key, value in data.items():
            setattr(profile, key, value)
        profile.save()
        return profile
    
    def get_profile_with_recent_activity(self, user):
        """Get a user's profile with recent activity"""
        profile = self.get_by_user(user)
        
        # Add recent activity data
        profile.recent_guides = user.guides.order_by('-created_at')[:5]
        profile.recent_forum_posts = user.forum_posts.order_by('-created_at')[:5]
        
        return profile