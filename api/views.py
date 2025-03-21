from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from datetime import date, timedelta

from .serializers import (
    User_Serializer,
    YourChild_Serializer,
    Milestone_Serializer,
    ParentsForum_Serializer,
    Comment_Serializer,
    ParentsGuide_Serializer,
    NutritionGuide_Serializer,
    Notification_Serializer,
    Contact_Serializer,
    VaccineCard_Serializer,
    Vaccine_Serializer,
    CalendarEvent_Serializer,
)
from tinySteps.models import (
    YourChild_Model,
    Milestone_Model,
    ParentsForum_Model,
    Guides_Model,
    Comment_Model,
    Notification_Model,
    Contact_Model,
    VaccineCard_Model,
    Vaccine_Model,
    CalendarEvent_Model,
)

###########################################################################
# PERMISOS PERSONALIZADOS
###########################################################################
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow owners or admins to edit objects
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions para cualquier request
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
        elif hasattr(obj, 'child'):
            return obj.child.user == request.user
            
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
        elif hasattr(obj, 'child'):
            return obj.child.user == request.user
            
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

class CurrentUser_View(APIView):
    """
    View to get the current user's information
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = User_Serializer(request.user)
        return Response(serializer.data)

class CurrentUserChildren_View(generics.ListAPIView):
    """
    View to get the current user's children
    """
    serializer_class = YourChild_Serializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return YourChild_Model.objects.filter(user=self.request.user)

###########################################################################
# NIÑOS Y HITOS DE DESARROLLO
###########################################################################
class YourChild_ViewSet(viewsets.ModelViewSet):
    serializer_class = YourChild_Serializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        return YourChild_Model.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class Milestone_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing milestones of the current user babies
    """
    serializer_class = Milestone_Serializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    
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

class ChildMilestone_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing milestones for a specific child
    """
    serializer_class = Milestone_Serializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        child_id = self.kwargs['child_pk']
        return Milestone_Model.objects.filter(
            child_id=child_id,
            child__user=self.request.user
        )
    
    def perform_create(self, serializer):
        child_id = self.kwargs['child_pk']
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
            forum.likes.remove(request.user)
            liked = False
        else:
            forum.likes.add(request.user)
            liked = True

        return Response({
            'liked': liked,
            'likes_count': forum.likes.count()
        })

class ForumComment_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on a specific forum post
    """
    serializer_class = Comment_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        forum_id = self.kwargs['forum_pk']
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=forum_id
        ).order_by('created_at')
    
    def perform_create(self, serializer):
        forum_id = self.kwargs['forum_pk']
        forum = get_object_or_404(ParentsForum_Model, id=forum_id)
        content_type = ContentType.objects.get_for_model(ParentsForum_Model)
        serializer.save(
            author=self.request.user,
            content_type=content_type,
            object_id=forum_id
        )

class Comment_ViewSet(viewsets.ModelViewSet):
    queryset = Comment_Model.objects.all()
    serializer_class = Comment_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    @action(detail=False, methods=['post'])
    def create_for_content(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, 
                           status=status.HTTP_401_UNAUTHORIZED)
        
        content_type_id = request.data.get('content_type_id')
        object_id = request.data.get('object_id')
        text = request.data.get('text')
        
        if not all([content_type_id, object_id, text]):
            return Response({'error': 'Missing required fields'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            model_class = content_type.model_class()
            target_object = model_class.objects.get(id=object_id)
            
            comment = Comment_Model.objects.create(
                content_type=content_type,
                object_id=object_id,
                author=request.user,
                text=text
            )
            
            serializer = self.get_serializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except (ContentType.DoesNotExist, model_class.DoesNotExist):
            return Response({'error': 'Invalid content type or object ID'}, 
                           status=status.HTTP_400_BAD_REQUEST)

###########################################################################
# GUÍAS PARA PADRES Y NUTRICIÓN
###########################################################################
class ParentsGuide_ViewSet(viewsets.ModelViewSet):
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

class NutritionGuide_ViewSet(viewsets.ModelViewSet):
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

class GuideComment_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on a specific guide
    """
    serializer_class = Comment_Serializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        guide_id = self.kwargs['guide_pk']
        content_type = ContentType.objects.get_for_model(Guides_Model)
        return Comment_Model.objects.filter(
            content_type=content_type,
            object_id=guide_id
        ).order_by('created_at')
    
    def perform_create(self, serializer):
        guide_id = self.kwargs['guide_pk']
        guide = get_object_or_404(Guides_Model, id=guide_id)
        content_type = ContentType.objects.get_for_model(Guides_Model)
        serializer.save(
            author=self.request.user,
            content_type=content_type,
            object_id=guide_id
        )

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
# SOLICITUDES DE INFORMACIÓN / CONTACTO
###########################################################################
class Contact_ViewSet(viewsets.ModelViewSet):
    serializer_class = Contact_Serializer
    queryset = Contact_Model.objects.all().order_by('-created_at')
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

###########################################################################
# VACUNA Y REGISTRO DE VACUNAS
###########################################################################
class VaccineCard_ViewSet(viewsets.ModelViewSet):
    serializer_class = VaccineCard_Serializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        return VaccineCard_Model.objects.filter(child__user=self.request.user)
    
    def perform_create(self, serializer):
        child_id = self.request.data.get('child')
        child = get_object_or_404(YourChild_Model, id=child_id, user=self.request.user)
        serializer.save(child=child)
    
    @action(detail=True, methods=['get'])
    def vaccines(self, request, pk=None):
        card = self.get_object()
        vaccines = card.vaccines.all()
        serializer = Vaccine_Serializer(vaccines, many=True)
        return Response(serializer.data)

class ChildVaccine_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vaccines for a specific child
    """
    serializer_class = Vaccine_Serializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    
    # Sobreescribir método get_queryset para filtrar por el niño para el que se está consultando
    def get_queryset(self):
        child_id = self.kwargs['child_pk']
        vaccine_card = get_object_or_404(
            VaccineCard_Model, 
            child_id=child_id,
            child__user=self.request.user
        )
        return Vaccine_Model.objects.filter(vaccine_card=vaccine_card)
    
    def perform_create(self, serializer):
        child_id = self.kwargs['child_pk']
        vaccine_card = get_object_or_404(
            VaccineCard_Model, 
            child_id=child_id,
            child__user=self.request.user
        )
        serializer.save(vaccine_card=vaccine_card)

###########################################################################
# CALENDARIO DE EVENTOS
###########################################################################
class ChildCalendarEvents_ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing calendar events for a specific child
    """
    serializer_class = CalendarEvent_Serializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        child_pk = self.kwargs['child_pk']
        # Opcionalmente filtrar por fechas si se proporcionan en query params
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')
        
        queryset = CalendarEvent_Model.objects.filter(child_id=child_pk, child__user=self.request.user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset.order_by('date', 'time')
    
    def perform_create(self, serializer):
        child_pk = self.kwargs['child_pk']
        child = get_object_or_404(YourChild_Model, id=child_pk, user=self.request.user)
        serializer.save(child=child)
    
    @action(detail=False, methods=['get'])
    def upcoming_events(self, request, child_pk=None):
        """Obtiene los próximos eventos y recordatorios para un niño"""
        child = get_object_or_404(YourChild_Model, id=child_pk, user=request.user)
        today = date.today()
        next_week = today + timedelta(days=7)
        
        # Eventos próximos
        upcoming_events = CalendarEvent_Model.objects.filter(
            child=child,
            date__gte=today,
            date__lte=next_week
        ).order_by('date', 'time')
        
        # Recordatorios (eventos con recordatorio activado)
        upcoming_reminders = upcoming_events.filter(has_reminder=True)
        
        # Estadísticas de eventos
        event_stats = {
            'doctor': CalendarEvent_Model.objects.filter(child=child, type='doctor').count(),
            'vaccine': CalendarEvent_Model.objects.filter(child=child, type='vaccine').count(),
            'milestone': CalendarEvent_Model.objects.filter(child=child, type='milestone').count(),
            'feeding': CalendarEvent_Model.objects.filter(child=child, type='feeding').count(),
            'other': CalendarEvent_Model.objects.filter(child=child, type='other').count(),
        }
        
        # Serializar datos
        events_serializer = self.get_serializer(upcoming_events, many=True)
        reminders_serializer = self.get_serializer(upcoming_reminders, many=True)
        
        return Response({
            'events': events_serializer.data,
            'reminders': reminders_serializer.data,
            'stats': event_stats
        })
    
    @action(detail=False, methods=['get'])
    def event_stats(self, request, child_pk=None):
        """Devuelve estadísticas de eventos para el panel de control"""
        child = get_object_or_404(YourChild_Model, id=child_pk, user=request.user)
        
        # Obtener recuento de eventos por tipo
        event_counts = CalendarEvent_Model.objects.filter(child=child)\
            .values('type')\
            .annotate(count=Count('id'))
        
        # Convertir a diccionario para fácil acceso
        stats = {
            'doctor': 0,
            'vaccine': 0,
            'milestone': 0,
            'feeding': 0,
            'other': 0,
            'total': 0
        }
        
        for item in event_counts:
            stats[item['type']] = item['count']
        
        # Calcular total
        stats['total'] = sum(stats.values())
        
        # Eventos próximos (para información adicional)
        today = date.today()
        upcoming_count = CalendarEvent_Model.objects.filter(
            child=child, 
            date__gte=today
        ).count()
        
        stats['upcoming'] = upcoming_count
        
        return Response(stats)

class CalendarEvent_ViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar eventos del calendario
    """
    serializer_class = CalendarEvent_Serializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Devuelve los eventos a los que tiene acceso el usuario actual"""
        return CalendarEvent_Model.objects.filter(child__user=self.request.user)
    
    def retrieve(self, request, pk=None):
        """Obtener un evento específico"""
        event = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Actualizar un evento existente"""
        event = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(event, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """Eliminar un evento"""
        event = get_object_or_404(self.get_queryset(), pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def update_date(self, request, pk=None):
        """
        Actualiza solo la fecha/hora de un evento (para drag & drop en calendario)
        """
        event = get_object_or_404(self.get_queryset(), pk=pk)
        
        # Extraer los datos de la solicitud
        new_date = request.data.get('date')
        new_time = request.data.get('time')
        all_day = request.data.get('allDay', False)
        
        if new_date:
            event.date = new_date
            
        if not all_day and new_time:
            event.time = new_time
        elif all_day:
            event.time = None
            
        event.save()
        serializer = self.get_serializer(event)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Valida que el niño pertenece al usuario antes de crear el evento"""
        child_id = self.request.data.get('child')
        try:
            child = YourChild_Model.objects.get(id=child_id, user=self.request.user)
            serializer.save()
        except YourChild_Model.DoesNotExist:
            raise ValueError("No tienes permiso para crear eventos para este niño")
        
###########################################################################
# BÚSQUEDA
###########################################################################
class Search_View(generics.ListAPIView):
    """
    View for searching across multiple content types
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        content_type = self.request.query_params.get('type', None)
        
        if content_type == 'forum':
            return ParentsForum_Serializer
        elif content_type == 'guide':
            return ParentsGuide_Serializer
        
        return ParentsForum_Serializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        content_type = self.request.query_params.get('type', None)
        
        if not query:
            return []
        
        if content_type == 'forum':
            return ParentsForum_Model.objects.filter(
                Q(title__icontains=query) | Q(desc__icontains=query)
            ).order_by('-created_at')
        elif content_type == 'parents_guide':
            return Guides_Model.objects.filter(
                Q(title__icontains=query) | Q(desc__icontains=query),
                guide_type='parent'
            ).order_by('-created_at')
        elif content_type == 'nutrition_guide':
            return Guides_Model.objects.filter(
                Q(title__icontains=query) | Q(desc__icontains=query),
                guide_type='nutrition'
            ).order_by('-created_at')
        else:
            forum_results = ParentsForum_Model.objects.filter(
                Q(title__icontains=query) | Q(desc__icontains=query)
            ).order_by('-created_at')[:5]
            
            guide_results = Guides_Model.objects.filter(
                Q(title__icontains=query) | Q(desc__icontains=query)
            ).order_by('-created_at')[:5]
            
            return forum_results
