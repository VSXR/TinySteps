import functools
from django.shortcuts import redirect
from django.http import JsonResponse

def ajax_required(view_func):
    """
    Decorator to ensure a view is only accessed via AJAX request.
    Returns a JSON error if not an AJAX request.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'This endpoint only accepts AJAX requests'
            }, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_or_403(view_func):
    """Decorator to ensure only staff users can access a view"""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Staff permission required'
                }, status=403)
            else:
                return redirect('permission_denied')
        return view_func(request, *args, **kwargs)
    return wrapper

def child_owner_required(view_func):
    """
    Decorator to ensure the logged in user is the owner of the child.
    Must be used with a view that has a 'pk' parameter for the child ID.
    """
    @functools.wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        from tinySteps.models import YourChild_Model
        
        try:
            child = YourChild_Model.objects.get(pk=pk)
            if child.user != request.user:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'You do not have permission to access this child'
                    }, status=403)
                else:
                    return redirect('permission_denied')
        except YourChild_Model.DoesNotExist:
            return redirect('not_found')
            
        return view_func(request, pk, *args, **kwargs)
    return wrapper