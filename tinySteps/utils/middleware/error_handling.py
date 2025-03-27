import logging
import traceback
from django.http import HttpResponse
from django.utils import timezone

logger = logging.getLogger('connection_errors')

class ErrorHandler_Middleware:
    """Middleware to handle connection errors like broken pipes and connection resets"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        """Process the request and return a response"""
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """Log connection errors and return a response to the client"""
        # Check if the exception is a connection error
        if isinstance(exception, (BrokenPipeError, ConnectionResetError)):
            client_ip = request.META.get('REMOTE_ADDR', 'unknown')
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            user = request.user.username if request.user.is_authenticated else 'anonymous'
            
            tb = traceback.format_exc()
            
            logger.warning(
                f"Connection error at {timezone.now()}\n"
                f"Error type: {type(exception).__name__}\n"
                f"Path: {request.path}\n"
                f"Method: {request.method}\n"
                f"Client IP: {client_ip}\n"
                f"User: {user}\n"
                f"User Agent: {user_agent}\n"
                f"Traceback: {tb}"
            )
            
            # Try to record the error if ConnectionError_Model exists
            try:
                from tinySteps.models import ConnectionError_Model
                ConnectionError_Model.objects.create(
                    error_type=type(exception).__name__,
                    path=request.path,
                    method=request.method,
                    client_ip=client_ip,
                    user=user,
                    user_agent=user_agent,
                    traceback=tb[:2000]
                )
            except ImportError:
                # Model doesn't exist, just log the error
                pass
            
            return HttpResponse("Connection broken. Please try again.", status=500)
        
        return None