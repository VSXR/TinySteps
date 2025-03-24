from django.shortcuts import render
from django.utils.translation import gettext as _
from ..models import ConnectionError_Model
import uuid
import logging

logger = logging.getLogger(__name__)

def custom_error_400(request, exception=None):
    """Handler for error 400 (Bad Request)"""
    return render(request, 'errors/errors.html', {
        'error_message': _('Bad request. The server could not understand your request.'),
        'error_code': 400
    }, status=400)

def custom_error_403(request, exception=None):
    """Handler for error 403 (Forbidden)"""
    return render(request, 'errors/errors.html', {
        'error_message': _('Access forbidden. You do not have permission to access this resource.'),
        'error_code': 403
    }, status=403)

def custom_error_404(request, exception=None):
    """Handler for error 404 (Not Found)"""
    return render(request, 'errors/errors.html', {
        'error_message': _('Page not found. The requested page does not exist.'),
        'error_code': 404
    }, status=404)

def custom_error_500(request):
    """Handler for error 500 (Server Error)"""
    error_id = None
    try:
        # This logs the error to database
        error_id = str(uuid.uuid4())[:8]
        ConnectionError_Model.objects.create(
            error_type="Server Error",
            path=request.path,
            method=request.method,
            client_ip=request.META.get('REMOTE_ADDR'),
            user=request.user.username if request.user.is_authenticated else '',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            traceback=error_id
        )
    except Exception as e:
        logger.error(f"Could not log error to database: {e}")
    
    return render(request, 'errors/errors.html', {
        'error_message': _('Server error. We apologize for the inconvenience.'),
        'error_code': f"500-{error_id}" if error_id else "500"
    }, status=500)

def database_error_view(request, error_message=None):
    """Utility function for database errors"""
    error_id = None
    try:
        # This logs the error to database
        error_id = str(uuid.uuid4())[:8]
        ConnectionError_Model.objects.create(
            error_type="Database Error",
            path=request.path,
            method=request.method,
            client_ip=request.META.get('REMOTE_ADDR'),
            user=request.user.username if request.user.is_authenticated else '',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            traceback=error_id
        )
    except Exception as e:
        logger.error(f"Could not log error to database: {e}")
    
    return render(request, 'errors/errors.html', {
        'error_message': error_message or _('Database connection error. Please try again later.'),
        'error_code': f"DB-{error_id}" if error_id else "DB"
    }, status=503)  # Service Unavailable