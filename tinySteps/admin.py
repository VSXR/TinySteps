from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from . import models
from .models import Notification_Model

# User and Children Models
@admin.register(models.YourChild_Model)
class YourChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date', 'age', 'gender', 'user')
    list_filter = ('gender',)
    search_fields = ('name', 'user__username', 'user__email')
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'second_name', 'birth_date', 'age', 'gender', 'user')
        }),
        ('Información física', {
            'fields': ('weight', 'height')
        }),
        ('Detalles adicionales', {
            'fields': ('image_url', 'desc')
        }),
    )

# Child Development Models
@admin.register(models.Milestone_Model)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'child', 'achieved_date')
    list_filter = ('child',)
    search_fields = ('title', 'description', 'child__name')
    date_hierarchy = 'achieved_date'
    fields = ('child', 'title', 'achieved_date', 'description', 'photo')

@admin.register(models.CalendarEvent_Model)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'child', 'type', 'date', 'time', 'has_reminder')
    list_filter = ('type', 'date', 'has_reminder')
    search_fields = ('title', 'description', 'child__name')
    date_hierarchy = 'date'
    
# Content Models
@admin.register(models.Guides_Model)
class GuidesAdmin(admin.ModelAdmin):
    list_display = ('title', 'guide_type', 'author', 'status', 'created_at', 'get_comments_count')
    list_filter = ('guide_type', 'status', 'created_at')
    search_fields = ('title', 'desc', 'author__username')
    readonly_fields = ('created_at', 'get_comments_count', 'preview_image')
    actions = ['approve_guides', 'reject_guides']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    get_comments_count.short_description = _('Comments')
    
    def preview_image(self, obj):
        if obj.image_url:
            return format_html(f'<img src="{obj.image_url}" width="150" />')
        return _("No image")
    preview_image.short_description = _('Preview')
    
    def approve_guides(self, request, queryset):
        updated = queryset.update(status='approved', approved_at=timezone.now())
        
        for guide in queryset:
            Notification_Model.objects.create(
                user=guide.author,
                message=_("Your guide '{0}' has been approved and is now published!").format(guide.title),
                url=guide.get_absolute_url()
            )
        
        self.message_user(request, ngettext(
            '%d guide was successfully approved.',
            '%d guides were successfully approved.',
            updated,
        ) % updated, messages.SUCCESS)
    approve_guides.short_description = _("Approve selected guides")
    
    def reject_guides(self, request, queryset):
        if 'apply' in request.POST:
            rejection_reason = request.POST.get('rejection_reason')
            updated = queryset.update(status='rejected', rejection_reason=rejection_reason)
            
            for guide in queryset:
                Notification_Model.objects.create(
                    user=guide.author,
                    message=_("Your guide '{0}' was not approved.").format(guide.title),
                    url=reverse('my_guides')
                )
            
            self.message_user(request, ngettext(
                '%d guide was rejected.',
                '%d guides were rejected.',
                updated,
            ) % updated, messages.SUCCESS)
            return
        
        context = {
            'title': _("Enter rejection reason"),
            'queryset': queryset,
            'action_checkbox_name': admin.ACTION_CHECKBOX_NAME,
            'opts': self.model._meta,
        }
        return render(request, 'admin/guides_reject_confirmation.html', context)
    reject_guides.short_description = _("Reject selected guides")
    
@admin.register(models.ParentsForum_Model)
class ParentsForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'get_likes_count', 'get_comments_count')
    list_filter = ('created_at',)
    search_fields = ('title', 'desc', 'author__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'get_likes_count', 'get_comments_count')
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = 'Likes'
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    get_comments_count.short_description = 'Comentarios'

# Interaction Models
@admin.register(models.Comment_Model)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text_preview', 'content_type', 'created_at')
    list_filter = ('created_at', 'content_type')
    search_fields = ('text', 'author__username')
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comentario'

# System Models
@admin.register(models.Notification_Model)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_preview', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('message', 'user__username')
    date_hierarchy = 'created_at'
    list_editable = ('read',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Mensaje'

@admin.register(models.Contact_Model)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message_preview')
    search_fields = ('name', 'email', 'message')
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Mensaje'

@admin.register(models.ConnectionError_Model)
class ConnectionErrorAdmin(admin.ModelAdmin):
    list_display = ('error_type', 'path', 'client_ip', 'user', 'timestamp')
    list_filter = ('error_type', 'timestamp')
    search_fields = ('path', 'client_ip', 'user')
    readonly_fields = ('error_type', 'path', 'method', 'client_ip', 'user', 
                      'user_agent', 'timestamp', 'traceback')
