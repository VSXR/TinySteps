import logging
from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

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

logger = logging.getLogger(__name__)

###########################################################################
# CUSTOM PERMISSIONS
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
# USER VIEWS
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
# CHILDREN AND DEVELOPMENT MILESTONES
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

class ChildGrowthData_ViewSet(LoginRequiredMixin, viewsets.ViewSet):
    """ViewSet for child growth data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_growth_data(self, request, child_pk=None):
        """Get growth data for a specific child"""
        logger.info(f"Fetching growth data for child ID: {child_pk}, User: {request.user.username}")
        
        try:
            child = get_object_or_404(YourChild_Model, pk=child_pk, user=request.user)
            logger.debug(f"Child found: {child.name} (ID: {child.id})")
            
            # Get growth data from child service
            from tinySteps.services.core.child_service import Child_Service
            child_service = Child_Service()
            data = child_service.get_growth_data(child_pk, request.user)
            
            logger.debug(f"Growth data retrieved successfully")
            return Response(data)
            
        except Exception as e:
            logger.error(f"Error fetching growth data for child {child_pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to retrieve growth data: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

###########################################################################
# FORUMS AND COMMENTS
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
# PARENT AND NUTRITION GUIDES
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
# NOTIFICATIONS
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
# CONTACT REQUESTS
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
# VACCINE AND VACCINE RECORDS
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
        vaccines = card.vaccines.all().order_by('-date')
        serializer = Vaccine_Serializer(vaccines, many=True)
        return Response({'vaccines': serializer.data})
    
    @action(detail=True, methods=['post'])
    def add_vaccine(self, request, pk=None):
        card = self.get_object()
        serializer = Vaccine_Serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(vaccine_card=card)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        card = self.get_object()
        vaccines = card.vaccines.all()
        
        total = vaccines.count()
        administered = vaccines.filter(administered=True).count()
        pending = total - administered
        
        # Upcoming vaccines are those with a next_dose_date in the future
        today = timezone.now().date()
        upcoming = vaccines.filter(next_dose_date__gte=today).count()
        
        return Response({
            'total': total,
            'administered': administered,
            'pending': pending,
            'upcoming': upcoming
        })
    
    @action(detail=True, methods=['get'])
    def upcoming(self, request, pk=None):
        card = self.get_object()
        today = timezone.now().date()
        
        # Get vaccines with next_dose_date in the future, ordered by date
        upcoming_vaccines = card.vaccines.filter(
            next_dose_date__gte=today
        ).order_by('next_dose_date')
        
        serializer = Vaccine_Serializer(upcoming_vaccines, many=True)
        return Response({'vaccines': serializer.data})

class Vaccine_ViewSet(viewsets.ModelViewSet):
    serializer_class = Vaccine_Serializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    
    def get_queryset(self):
        return Vaccine_Model.objects.filter(vaccine_card__child__user=self.request.user)
    
    def perform_create(self, serializer):
        vaccine_card_id = self.request.data.get('vaccine_card')
        vaccine_card = get_object_or_404(
            VaccineCard_Model, 
            id=vaccine_card_id, 
            child__user=self.request.user
        )
        serializer.save(vaccine_card=vaccine_card)

###########################################################################
# CALENDAR EVENTS
###########################################################################
class ChildCalendarEvents_ViewSet(LoginRequiredMixin, viewsets.ViewSet):
    """ViewSet for calendar events by child"""
    
    def list(self, request, child_pk=None):
        """Get all events for a child"""
        logger.info(f"Fetching events for child ID: {child_pk}, User: {request.user.username}")
        
        try:
            child = get_object_or_404(YourChild_Model, pk=child_pk, user=request.user)
            logger.debug(f"Child found: {child.name} (ID: {child.id})")
            
            # Get optional date range filters
            start_date_str = request.query_params.get('start')
            end_date_str = request.query_params.get('end')
            logger.debug(f"Date range filters - Start: {start_date_str}, End: {end_date_str}")
            
            # Filter events by date range if provided
            events = CalendarEvent_Model.objects.filter(child=child)
            
            if start_date_str:
                # Extract just the date part (YYYY-MM-DD) from the ISO8601 string
                if 'T' in start_date_str:
                    start_date = start_date_str.split('T')[0]
                else:
                    start_date = start_date_str
                events = events.filter(date__gte=start_date)
                logger.debug(f"Filtered by start date: {start_date}, Events count: {events.count()}")
                
            if end_date_str:
                # Extract just the date part (YYYY-MM-DD) from the ISO8601 string
                if 'T' in end_date_str:
                    end_date = end_date_str.split('T')[0]
                else:
                    end_date = end_date_str
                events = events.filter(date__lte=end_date)
                logger.debug(f"Filtered by end date: {end_date}, Events count: {events.count()}")
            
            serializer = CalendarEvent_Serializer(events, many=True)
            logger.info(f"Returning {len(serializer.data)} events for child {child_pk}")
            return Response({'events': serializer.data})
        
        except Exception as e:
            logger.error(f"Error fetching events for child {child_pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to retrieve events: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, child_pk=None):
        """Create a new event for a child"""
        logger.info(f"Creating new event for child ID: {child_pk}, User: {request.user.username}")
        logger.debug(f"Request data: {request.data}")
        
        try:
            child = get_object_or_404(YourChild_Model, pk=child_pk, user=request.user)
            logger.debug(f"Child found: {child.name} (ID: {child.id})")
            
            # Add child to request data
            data = request.data.copy()
            data['child'] = child.id
            
            serializer = CalendarEvent_Serializer(data=data)
            if serializer.is_valid():
                event = serializer.save()
                logger.info(f"Event created successfully. Event ID: {event.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Invalid event data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating event for child {child_pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to create event: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def upcoming_events(self, request, child_pk=None):
        """Get upcoming events with reminders"""
        logger.info(f"Fetching upcoming events for child ID: {child_pk}")
        
        try:
            child = get_object_or_404(YourChild_Model, pk=child_pk, user=request.user)
            today = timezone.now().date()
            
            # Get events in the next 30 days with reminders
            events = CalendarEvent_Model.objects.filter(
                child=child,
                date__gte=today,
                date__lte=today + timedelta(days=30),
                has_reminder=True
            ).order_by('date', 'time')
            
            logger.debug(f"Found {events.count()} upcoming events with reminders")
            serializer = CalendarEvent_Serializer(events, many=True)
            return Response({'reminders': serializer.data})
            
        except Exception as e:
            logger.error(f"Error fetching upcoming events for child {child_pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to retrieve upcoming events: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def event_stats(self, request, child_pk=None):
        """Get event statistics for a child"""
        logger.info(f"Fetching event statistics for child ID: {child_pk}")
        
        try:
            child = get_object_or_404(YourChild_Model, pk=child_pk, user=request.user)
            
            stats = {
                'total': CalendarEvent_Model.objects.filter(child=child).count(),
                'doctor': CalendarEvent_Model.objects.filter(child=child, type='doctor').count(),
                'vaccine': CalendarEvent_Model.objects.filter(child=child, type='vaccine').count(),
                'milestone': CalendarEvent_Model.objects.filter(child=child, type='milestone').count(),
                'feeding': CalendarEvent_Model.objects.filter(child=child, type='feeding').count(),
                'other': CalendarEvent_Model.objects.filter(child=child, type='other').count(),
            }
            
            logger.debug(f"Event statistics: {stats}")
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error fetching event stats for child {child_pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to retrieve event statistics: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CalendarEvent_ViewSet(LoginRequiredMixin, viewsets.ViewSet):
    """ViewSet for individual calendar events"""
    
    def retrieve(self, request, pk=None):
        """Get a specific event"""
        logger.info(f"Retrieving event ID: {pk} for user: {request.user.username}")
        
        try:
            event = get_object_or_404(CalendarEvent_Model, pk=pk, child__user=request.user)
            serializer = CalendarEvent_Serializer(event)
            logger.debug(f"Event retrieved successfully: {event.title}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving event {pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to retrieve event: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """Update a specific event"""
        logger.info(f"Updating event ID: {pk} for user: {request.user.username}")
        logger.debug(f"Update data: {request.data}")
        
        try:
            event = get_object_or_404(CalendarEvent_Model, pk=pk, child__user=request.user)
            serializer = CalendarEvent_Serializer(event, data=request.data, partial=True)
            
            if serializer.is_valid():
                updated_event = serializer.save()
                logger.info(f"Event updated successfully: {updated_event.title}")
                return Response(serializer.data)
            else:
                logger.warning(f"Invalid update data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error updating event {pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to update event: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, pk=None):
        """Delete a specific event"""
        logger.info(f"Deleting event ID: {pk} for user: {request.user.username}")
        
        try:
            event = get_object_or_404(CalendarEvent_Model, pk=pk, child__user=request.user)
            event_title = event.title  # Save for logging
            event.delete()
            logger.info(f"Event '{event_title}' (ID: {pk}) deleted successfully")
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"Error deleting event {pk}: {str(e)}", exc_info=True)
            return Response(
                {'error': f"Failed to delete event: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

###########################################################################
# SEARCH
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
