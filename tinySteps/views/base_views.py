from django.shortcuts import render
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)

class BaseView:
    @staticmethod
    def handle_exception(request, exception, default_message, error_code):
        logger.error(f"Error {error_code}: {str(exception)}")
        return render(request, 'errors/errors.html', {
            'error_message': _(default_message),
            'error_code': error_code
        }, status=500)