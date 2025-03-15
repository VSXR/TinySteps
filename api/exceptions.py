import logging
import traceback
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.views import exception_handler

from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    ValidationError,
    Throttled,
)

# Configuración de logger
logger = logging.getLogger('api_exceptions')

# Custom API exceptions
class ChildNotFound(NotFound):
    default_detail = "El niño no fue encontrado o no tienes permiso para acceder a él."

class ResourceAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "El recurso ya existe."
    default_code = 'resource_already_exists'

class RelatedObjectDoesNotExist(NotFound):
    default_detail = "Un objeto relacionado necesario no existe."
    default_code = 'related_object_not_found'

class VaccineCardNotFound(NotFound):
    default_detail = "La cartilla de vacunación no fue encontrada."
    default_code = 'vaccine_card_not_found'

class EventNotFound(NotFound):
    default_detail = "El evento no fue encontrado."
    default_code = 'event_not_found'

def handle_django_validation_error(exc):
    """Maneja errores de validación de Django"""
    from rest_framework.response import Response
    
    error_dict = {'status': 'error', 'type': 'validation_error', 'code': status.HTTP_400_BAD_REQUEST}
    
    if hasattr(exc, 'message_dict'):
        error_dict['details'] = exc.message_dict
    else:
        error_dict['message'] = exc.messages[0] if exc.messages else "Error de validación"
    
    return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)

def handle_integrity_error(exc):
    """Maneja errores de integridad de la base de datos"""
    from rest_framework.response import Response
    
    error_dict = {
        'status': 'error',
        'type': 'database_error',
        'code': status.HTTP_400_BAD_REQUEST,
        'message': "Error de integridad en la base de datos"
    }
    
    if settings.DEBUG:
        error_dict['debug'] = {'details': str(exc)}
    
    return Response(error_dict, status=status.HTTP_400_BAD_REQUEST)

def handle_generic_exception(exc):
    """Maneja excepciones genéricas no controladas"""
    from rest_framework.response import Response
    
    logger.exception("Excepción no controlada", exc_info=exc)
    
    error_dict = {
        'status': 'error',
        'type': 'server_error',
        'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'message': "Error interno del servidor"
    }
    
    if settings.DEBUG:
        error_dict['debug'] = {
            'exception_class': exc.__class__.__name__,
            'details': str(exc),
            'traceback': traceback.format_exc()
        }
    
    return Response(error_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones que proporciona respuestas
    estandarizadas y detalladas para diferentes tipos de errores.
    """
    # Primero usamos el manejador predeterminado para obtener la respuesta
    response = exception_handler(exc, context)
    
    # Si hay una respuesta del manejador predeterminado
    if response is not None:
        error_data = {
            'status': 'error',
            'code': response.status_code,
        }
        
        # Registrar el error con información de contexto
        request = context.get('request')
        if request:
            logger.error(
                f"Error API: {exc} - Endpoint: {request.path} - Método: {request.method}"
            )
        
        # Personalizar respuesta según el tipo de error
        if isinstance(exc, ValidationError):
            # Para errores de validación, incluir detalles de cada campo
            error_data['message'] = "Error de validación"
            error_data['details'] = response.data
            error_data['type'] = 'validation_error'
            
        elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            error_data['message'] = "Autenticación requerida"
            error_data['type'] = 'authentication_error'
            
        elif isinstance(exc, PermissionDenied):
            error_data['message'] = "No tienes permiso para realizar esta acción"
            error_data['type'] = 'permission_error'
            
        elif isinstance(exc, NotFound):
            error_data['message'] = "El recurso solicitado no existe"
            error_data['type'] = 'not_found'
            
        elif isinstance(exc, MethodNotAllowed):
            error_data['message'] = f"Método {request.method if request else 'desconocido'} no permitido"
            error_data['type'] = 'method_not_allowed'
            
        elif isinstance(exc, Throttled):
            error_data['message'] = "Has excedido el límite de peticiones"
            error_data['type'] = 'throttled'
            wait_time = exc.wait
            if wait_time:
                error_data['wait_seconds'] = wait_time
                
        else:
            # Para otros errores de la API
            error_data['message'] = response.data.get('detail', str(exc))
            error_data['type'] = 'api_error'
        
        # En modo debug, agregar información adicional
        if settings.DEBUG:
            error_data['debug'] = {
                'exception_class': exc.__class__.__name__,
                'traceback': traceback.format_exc(),
            }
            
        response.data = error_data
    else:
        # Manejo de errores no manejados por DRF
        if isinstance(exc, DjangoValidationError):
            response = handle_django_validation_error(exc)
        elif isinstance(exc, IntegrityError):
            response = handle_integrity_error(exc)
        else:
            response = handle_generic_exception(exc)
    
    return response