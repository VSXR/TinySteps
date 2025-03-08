from django.contrib import admin
from django.utils.html import format_html
from . import models

# Niños
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

# Hitos de desarrollo
@admin.register(models.Milestone_Model)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'child', 'achieved_date')
    list_filter = ('child',)
    search_fields = ('title', 'description', 'child__name')
    date_hierarchy = 'achieved_date'
    fields = ('child', 'title', 'achieved_date', 'description', 'photo')

# Foros
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

# Guías
@admin.register(models.Guides_Model)
class GuidesAdmin(admin.ModelAdmin):
    list_display = ('title', 'guide_type', 'created_at', 'get_comments_count')
    list_filter = ('guide_type', 'created_at')
    search_fields = ('title', 'desc', 'author')
    readonly_fields = ('created_at', 'get_comments_count', 'preview_image')
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    get_comments_count.short_description = 'Comentarios'
    
    def preview_image(self, obj):
        if obj.image_url:
            return format_html(f'<img src="{obj.image_url}" width="150" />')
        return "Sin imagen"
    preview_image.short_description = 'Vista previa'

# Comentarios
@admin.register(models.Comment_Model)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text_preview', 'content_type', 'created_at')
    list_filter = ('created_at', 'content_type')
    search_fields = ('text', 'author__username')
    date_hierarchy = 'created_at'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comentario'

# Notificaciones
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

# Solicitudes de información
@admin.register(models.InfoRequest_Model)
class InfoRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message_preview')
    search_fields = ('name', 'email', 'message')
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Mensaje'