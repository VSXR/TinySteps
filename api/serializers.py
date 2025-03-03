from rest_framework import serializers
from django.contrib.auth.models import User

from tinySteps.models import (
    YourChild_Model, 
    Milestone_Model, 
    ParentsForum_Model,
    ParentsGuides_Model,
    NutritionGuides_Model,
    Comment_Model,
    Notification_Model,
    InfoRequest_Model
)

class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

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

class ParentsGuide_Serializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ParentsGuides_Model
        fields = ['id', 'title', 'content', 'image', 'created_at', 'comments_count']
        
    def get_comments_count(self, obj):
        return obj.comments.count()

class NutritionGuide_Serializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NutritionGuides_Model
        fields = ['id', 'title', 'content', 'image', 'created_at', 'comments_count']
        
    def get_comments_count(self, obj):
        return obj.comments.count()

class Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notification_Model
        fields = ['id', 'title', 'message', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']

class InfoRequest_Serializer(serializers.ModelSerializer):
    class Meta:
        model = InfoRequest_Model
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']