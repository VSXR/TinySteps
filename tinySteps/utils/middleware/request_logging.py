import logging
import time

logger = logging.getLogger('request')

class RequestLogging_Middleware:
    """Middleware to log request information and response time"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Log request information
        self._log_request(request)
        
        # Start a timer to calculate request time and calculate the response time
        start_time = time.time()
        response = self.get_response(request)
        request_time = time.time() - start_time
        self._log_response(request, response, request_time)
        
        return response
        
    def _log_request(self, request):
        """Log the request information"""
        path = request.path
        method = request.method
        user = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
        
        logger.info(f"REQUEST: {method} {path} from user={user}")
        
    def _log_response(self, request, response, request_time):
        """Log the response information"""
        path = request.path
        method = request.method
        status = response.status_code
        
        logger.info(f"RESPONSE: {method} {path} completed with status={status} in {request_time:.3f}s")