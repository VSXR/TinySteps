from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views
app_name = 'api'

# Main router
router = DefaultRouter()
router.register(r'users', views.User_ViewSet, basename='user')
router.register(r'children', views.YourChild_ViewSet, basename='child')
router.register(r'vaccine-cards', views.VaccineCard_ViewSet, basename='vaccine-card')
router.register(r'vaccines', views.Vaccine_ViewSet, basename='vaccines')
router.register(r'calendar-events', views.CalendarEvent_ViewSet, basename='calendar-event')
router.register(r'milestones', views.Milestone_ViewSet, basename='milestone')
router.register(r'forums', views.ParentsForum_ViewSet, basename='forum')
router.register(r'comments', views.Comment_ViewSet, basename='comment')
router.register(r'parents-guides', views.ParentsGuide_ViewSet, basename='parents-guide')
router.register(r'nutrition_guides', views.NutritionGuide_ViewSet, basename='nutrition-guide')
router.register(r'notifications', views.Notification_ViewSet, basename='notification')
router.register(r'info-requests', views.Contact_ViewSet, basename='info-request')

# Nested routers
children_router = routers.NestedSimpleRouter(router, r'children', lookup='child')
children_router.register(r'events', views.ChildCalendarEvents_ViewSet, basename='child-events')
children_router.register(r'milestones', views.ChildMilestone_ViewSet, basename='child-milestone')

# Routers for forums and guides
forum_router = routers.NestedSimpleRouter(router, r'forums', lookup='forum')
forum_router.register(r'comments', views.ForumComment_ViewSet, basename='forum-comment')

parents_guide_router = routers.NestedSimpleRouter(router, r'parents-guides', lookup='guide')
parents_guide_router.register(r'comments', views.GuideComment_ViewSet, basename='parents-guide-comment')

nutrition_guide_router = routers.NestedSimpleRouter(router, r'nutrition_guides', lookup='guide')
nutrition_guide_router.register(r'comments', views.GuideComment_ViewSet, basename='nutrition-guide-comment')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(children_router.urls)),
    path('', include(forum_router.urls)),
    path('', include(parents_guide_router.urls)),
    path('', include(nutrition_guide_router.urls)),
    path('auth/', include('rest_framework.urls')),

    # Custom views
    path('me/', views.CurrentUser_View.as_view(), name='current-user'),
    path('my-children/', views.CurrentUserChildren_View.as_view(), name='current-user-children'),
    path('search/', views.Search_View.as_view(), name='search'),

    # Calendar event API endpoints
    path('children/<int:child_pk>/events/', 
         views.ChildCalendarEvents_ViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='child-calendar-events'),
    path('children/<int:child_pk>/events/upcoming_events/', 
         views.ChildCalendarEvents_ViewSet.as_view({'get': 'upcoming_events'}), 
         name='child-upcoming-events'),
    path('children/<int:child_pk>/events/event_stats/', 
         views.ChildCalendarEvents_ViewSet.as_view({'get': 'event_stats'}), 
         name='child-event-stats'),
    path('calendar-events/<int:pk>/', 
         views.CalendarEvent_ViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), 
         name='calendar-event-detail'),
    path('calendar-events/<int:pk>/update-date/', 
         views.CalendarEvent_ViewSet.as_view({'post': 'update_date'}), 
         name='calendar-event-update-date'),
    path('children/<int:child_pk>/growth-data/', 
        views.ChildGrowthData_ViewSet.as_view({'get': 'get_growth_data'}), 
        name='child-growth-data'),
]
