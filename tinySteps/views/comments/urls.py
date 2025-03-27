from django.urls import path
from . import comment_views

app_name = 'comments' 

urlpatterns = [
    path('add/<str:content_type>/<int:object_id>/', comment_views.add_comment, name='add'),
    path('delete/<int:comment_id>/', comment_views.delete_comment, name='delete'),
    path('list/<str:content_type>/<int:object_id>/', comment_views.list_comments, name='list'),
]