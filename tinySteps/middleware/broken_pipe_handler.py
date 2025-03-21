import logging
import traceback
from django.http import HttpResponse
from django.utils import timezone
from tinySteps.models import ConnectionError_Model

logger = logging.getLogger('connection_errors')

class BrokenPipeHandlerMiddleware:
    """
    Middleware to handle broken pipe errors and connection reset errors
    When a broken pipe error or a connection reset error occurs, the middleware logs the error and saves it to the database
    The middleware returns a 499 status code to the client
    The middleware is added to the MIDDLEWARE setting in settings.py!
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
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
            
            ConnectionError_Model.objects.create(
                error_type=type(exception).__name__,
                path=request.path,
                method=request.method,
                client_ip=client_ip,
                user=user,
                user_agent=user_agent,
                traceback=tb
            )
            
            return HttpResponse("Connection closed", status=499)
        return None