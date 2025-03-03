from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from .serializers import (
    User_Serializer,
    YourChild_Serializer,
    Milestone_Serializer,
    ParentsForum_Serializer,
    Comment_Serializer,
    ParentsGuide_Serializer,
    NutritionGuide_Serializer,
    Notification_Serializer,
    InfoRequest_Serializer
)

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

# Custom permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
            
        return False

# Child API views
class YourChild_ViewSet(viewsets.ModelViewSet):
    serializer_class = YourChild_Serializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return YourChild_Model.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Cambiado de MilestoneViewSet a Milestone_ViewSet para mantener consistencia de nombres
class Milestone_ViewSet(viewsets.ModelViewSet):
    serializer_class = Milestone_Serializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        child_id = self.request.query_params.get('child', None)
        queryset = Milestone_Model.objects.all()
        
        if child_id:
            queryset = queryset.filter(child_id=child_id)
            
        return queryset.filter(child__user=self.request.user)
    
    def perform_create(self, serializer):
        child_id = self.request.data.get('child')
        child = get_object_or_404(YourChild_Model, id=child_id, user=self.request.user)
        serializer.save(child=child)

# Forum API views
class ParentsForum_ViewSet(viewsets.ModelViewSet):
    serializer_class = ParentsForum_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return ParentsForum_Model.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        forum = self.get_object()
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'Comment text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get content type for forum model
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        
        # Create comment
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=forum.id,
            author=request.user,
            text=text
        )
        
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        forum = self.get_object()
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        comments = Comment_Model.objects.filter(
            content_type=content_type,
            object_id=forum.id
        ).order_by('created_at')
        
        serializer = Comment_Serializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        forum = self.get_object()

        # Check if user already liked this post
        if forum.likes.filter(id=request.user.id).exists():
            # Unlike the post
            forum.likes.remove(request.user)
            liked = False
        else:
            # Like the post
            forum.likes.add(request.user)
            liked = True

        return Response({
            'liked': liked,
            'likes_count': forum.likes.count()
        })

# Guides API views
class ParentsGuide_ViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ParentsGuides_Model.objects.all().order_by('-created_at')
    serializer_class = ParentsGuide_Serializer
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        guide = self.get_object()
        content_type = ContentType.objects.get_for_model(ParentsGuides_Model)
        comments = Comment_Model.objects.filter(
            content_type=content_type,
            object_id=guide.id
        ).order_by('created_at')
        
        serializer = Comment_Serializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        guide = self.get_object()
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'Comment text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get content type for guide model
        content_type = ContentType.objects.get_for_model(ParentsGuides_Model)
        
        # Create comment
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=guide.id,
            author=request.user,
            text=text
        )
        
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class NutritionGuide_ViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NutritionGuides_Model.objects.all().order_by('-created_at')
    serializer_class = NutritionGuide_Serializer
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        guide = self.get_object()
        content_type = ContentType.objects.get_for_model(NutritionGuides_Model)
        comments = Comment_Model.objects.filter(
            content_type=content_type,
            object_id=guide.id
        ).order_by('created_at')
        
        serializer = Comment_Serializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        guide = self.get_object()
        text = request.data.get('text', '')
        
        if not text:
            return Response(
                {'error': 'Comment text is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get content type for guide model
        content_type = ContentType.objects.get_for_model(NutritionGuides_Model)
        
        # Create comment
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=guide.id,
            author=request.user,
            text=text
        )
        
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Notification API views
class Notification_ViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = Notification_Serializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification_Model.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

# Info Request API views
class InfoRequest_ViewSet(viewsets.ModelViewSet):
    serializer_class = InfoRequest_Serializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]