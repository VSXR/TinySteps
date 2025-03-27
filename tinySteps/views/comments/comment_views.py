from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from tinySteps.factories import CommentService_Factory

comment_service = CommentService_Factory.create_service()

@login_required
def add_comment(request, content_type, object_id):
    """Add a comment to a content object"""
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        if not content.strip():
            return JsonResponse({'success': False, 'error': 'Comment text is required'})
            
        try:
            comment_service.add_comment(
                content_type_str=content_type,
                object_id=object_id,
                content=content,
                user=request.user
            )
            
            # Determinar la URL de redirección basada en el tipo de contenido
            if content_type == 'parent_guide':
                return redirect('parent_guide_detail', pk=object_id)
            elif content_type == 'nutrition_guide':
                return redirect('nutrition_guide_detail', pk=object_id)
            elif content_type == 'forum_post':
                return redirect('view_post', post_id=object_id)
            else:
                return redirect('index')
                
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def delete_comment(request, comment_id):
    """Delete a comment"""
    if request.method == 'POST':
        try:
            success = comment_service.delete_comment(comment_id, request.user)
            if success:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                return redirect(request.META.get('HTTP_REFERER', 'index'))
            else:
                return JsonResponse({'success': False, 'error': 'Cannot delete comment'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def list_comments(request, content_type, object_id):
    """List comments for a content object"""
    try:
        comments = comment_service.get_comments(content_type, object_id)
        # Convertir a formato JSON si es necesario
        return JsonResponse({
            'success': True,
            'comments': [comment.to_dict() for comment in comments]
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})