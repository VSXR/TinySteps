from rest_framework import serializers
from django.contrib.auth.models import User

from tinySteps.models import (
    YourChild_Model, 
    Milestone_Model, 
    ParentsForum_Model,
    Guides_Model,
    Comment_Model,
    Notification_Model,
    Contact_Model,
    Vaccine_Model,
    VaccineCard_Model,
    CalendarEvent_Model,
)

###########################################################################
# USER SERIALIZERS
###########################################################################
class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

###########################################################################
# CHILD AND DEVELOPMENT SERIALIZERS
###########################################################################
class YourChild_Serializer(serializers.ModelSerializer):
    class Meta:
        model = YourChild_Model
        fields = '__all__'
        read_only_fields = ['id', 'user']

class Milestone_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone_Model
        fields = '__all__'
        read_only_fields = ['id']

###########################################################################
# COMMUNICATION SERIALIZERS
###########################################################################
class Comment_Serializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment_Model
        fields = ['id', 'author', 'author_name', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
        
    def get_author_name(self, obj):
        return obj.author.username if obj.author else "Anonymous"

class ParentsForum_Serializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ParentsForum_Model
        fields = ['id', 'title', 'desc', 'created_at', 'author', 'author_name', 'comments_count', 'likes_count']
        read_only_fields = ['id', 'created_at', 'author', 'author_name', 'comments_count', 'likes_count']
        
    def get_author_name(self, obj):
        return obj.author.username
        
    def get_comments_count(self, obj):
        return obj.comments.count()
        
    def get_likes_count(self, obj):
        return obj.likes.count()

class Contact_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Model
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

class Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notification_Model
        fields = ['id', 'title', 'message', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']

###########################################################################
# EDUCATIONAL CONTENT SERIALIZERS
###########################################################################
class ParentsGuide_Serializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Guides_Model
        fields = ['id', 'title', 'desc', 'image_url', 'created_at', 'comments_count']
        read_only_fields = ['id', 'created_at']
        
    def get_comments_count(self, obj):
        return obj.comments.count()

class NutritionGuide_Serializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Guides_Model
        fields = ['id', 'title', 'desc', 'image_url', 'created_at', 'comments_count']
        read_only_fields = ['id', 'created_at']
        
    def get_comments_count(self, obj):
        return obj.comments.count()

###########################################################################
# HEALTH AND MEDICAL SERIALIZERS
###########################################################################
class Vaccine_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine_Model
        fields = ['id', 'name', 'date', 'notes', 'administered', 'next_dose_date']
        read_only_fields = ['id']

class VaccineCard_Serializer(serializers.ModelSerializer):
    vaccines = Vaccine_Serializer(many=True, read_only=True)
    
    class Meta:
        model = VaccineCard_Model
        fields = ['id', 'child', 'created_at', 'updated_at', 'vaccines']
        read_only_fields = ['id', 'created_at', 'updated_at']

###########################################################################
# PLANNING SERIALIZERS
###########################################################################
class CalendarEvent_Serializer(serializers.ModelSerializer):
    event_color = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarEvent_Model
        fields = ['id', 'child', 'title', 'type', 'date', 'time', 'location', 'description', 
                  'has_reminder', 'reminder_minutes', 'created_at', 'updated_at',
                  'event_color']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_event_color(self, obj):
        return obj.get_event_color()