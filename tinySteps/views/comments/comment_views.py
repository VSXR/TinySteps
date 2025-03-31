from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext as _
from tinySteps.factories import CommentService_Factory

comment_service = CommentService_Factory.create_service()

@login_required
def add_comment(request, content_type, object_id):
    """Add a comment to a content object"""
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        if not content.strip():
            messages.error(request, _("Comment text is required"))
            return redirect(request.META.get('HTTP_REFERER', '/'))
            
        try:
            comment_service.add_comment(
                content_type_str=content_type,
                object_id=object_id,
                content=content,
                user=request.user
            )
            
            if content_type == 'parent_guide':
                return redirect('parent_guide_details', pk=object_id)
            elif content_type == 'nutrition_guide':
                return redirect('nutrition_guide_details', pk=object_id)
            elif content_type == 'forum_post':
                return redirect('forum:view_post', post_id=object_id)
            else:
                return redirect('guides')
                
        except ValueError as e:
            messages.error(request, str(e))
            return redirect(request.META.get('HTTP_REFERER', '/'))
    
    messages.error(request, _("Invalid request"))
    return redirect('guides')

@login_required
def delete_comment(request, comment_id):
    """Delete a comment"""
    if request.method == 'POST':
        success = comment_service.delete_comment(comment_id, request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': _("You don't have permission to delete this comment")})
        
        # For non-AJAX requests
        if success:
            messages.success(request, _("Comment deleted successfully"))
        else:
            messages.error(request, _("You don't have permission to delete this comment"))
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

def list_comments(request, content_type, object_id):
    """List comments for a content object in JSON format if we need it"""
    try:
        comments = comment_service.get_comments(content_type, object_id)
        return JsonResponse({
            'success': True,
            'comments': [comment.to_dict() for comment in comments]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})