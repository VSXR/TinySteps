from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.User_ViewSet, basename='user') if hasattr(views, 'User_ViewSet') else None
router.register(r'children', views.YourChild_ViewSet, basename='child')
router.register(r'milestones', views.Milestone_ViewSet, basename='milestone')
router.register(r'forums', views.ParentsForum_ViewSet, basename='forum')
router.register(r'parents-guides', views.ParentsGuide_ViewSet, basename='parent-guide')
router.register(r'nutrition-guides', views.NutritionGuide_ViewSet, basename='nutrition-guide')
router.register(r'notifications', views.Notification_ViewSet, basename='notification')
router.register(r'info-requests', views.InfoRequest_ViewSet, basename='info-request')

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]