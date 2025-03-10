from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.contrib import messages

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
    Guides_Model,
    Comment_Model,
    Notification_Model,
    InfoRequest_Model
)

###########################################################################
# PERMISOS PERSONALIZADOS
###########################################################################
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow owners or admins to edit objects
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Si el usuario es administrador, permitir cualquier operación
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
            
        return False
    
class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission para permitir:
    - Lectura a cualquier usuario autenticado
    - Escritura al propietario
    - Todas las acciones a administradores
    """
    def has_permission(self, request, view):
        # Permitir GET, HEAD, OPTIONS a cualquier usuario
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
            
        # Permitir POST a usuarios autenticados y administradores
        if request.method == 'POST':
            return request.user.is_authenticated
            
        # Para otros métodos (PUT, PATCH, DELETE), comprobar permisos a nivel de objeto
        return True
    
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para cualquier request autenticada
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Los administradores pueden hacer cualquier cosa
        if request.user.is_staff or request.user.is_superuser:
            return True

        # El propietario puede editar sus propios objetos
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
            
        return False

###########################################################################
# USUARIOS
###########################################################################
class User_ViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = User_Serializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint for getting the current authenticated user's information"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

###########################################################################
# NIÑOS Y HITOS DE DESARROLLO
###########################################################################
class YourChild_ViewSet(viewsets.ModelViewSet):
    serializer_class = YourChild_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        return YourChild_Model.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class Milestone_ViewSet(viewsets.ModelViewSet):
    serializer_class = Milestone_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
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

###########################################################################
# FOROS Y COMENTARIOS
###########################################################################
class ParentsForum_ViewSet(viewsets.ModelViewSet):
    serializer_class = ParentsForum_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        return ParentsForum_Model.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_comment(request, model_type, pk):
        if model_type == 'forum':
            obj = get_object_or_404(ParentsForum_Model, pk=pk)
        elif model_type == 'parent_guide':
            obj = get_object_or_404(Guides_Model, pk=pk, guide_type='parent')
        elif model_type == 'nutrition_guide':
            obj = get_object_or_404(Guides_Model, pk=pk, guide_type='nutrition')
        else:
            raise Http404("Invalid content type")
        
        if request.method == 'POST':
            text = request.POST.get('text')
            if text:
                Comment_Model.objects.create(
                    content_object=obj,
                    author=request.user,
                    text=text
                )
                messages.success(request, "Comment added successfully.")
            return redirect(obj.get_absolute_url())
        
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

###########################################################################
# GUÍAS PARA PADRES Y NUTRICIÓN
###########################################################################
class ParentsGuide_ViewSet(viewsets.ModelViewSet):  # Cambiar de ReadOnlyModelViewSet a ModelViewSet
    queryset = Guides_Model.objects.filter(guide_type='parent').order_by('-created_at')
    serializer_class = ParentsGuide_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        guide = self.get_object()
        content_type = ContentType.objects.get_for_model(Guides_Model)
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
            
        content_type = ContentType.objects.get_for_model(Guides_Model)
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=guide.id,
            author=request.user,
            text=text
        )
        
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            
        forum = self.get_object()
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


class NutritionGuide_ViewSet(viewsets.ModelViewSet):  # Cambiar de ReadOnlyModelViewSet a ModelViewSet
    queryset = Guides_Model.objects.filter(guide_type='nutrition').order_by('-created_at')
    serializer_class = NutritionGuide_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        guide = self.get_object()
        content_type = ContentType.objects.get_for_model(Guides_Model)
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
            
        content_type = ContentType.objects.get_for_model(Guides_Model)
        comment = Comment_Model.objects.create(
            content_type=content_type,
            object_id=guide.id,
            author=request.user,
            text=text
        )
        
        serializer = Comment_Serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

###########################################################################
# NOTIFICACIONES
###########################################################################
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

###########################################################################
# SOLICITUDES DE INFORMACIÓN
###########################################################################
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