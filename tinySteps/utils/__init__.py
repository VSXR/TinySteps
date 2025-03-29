"""Utils package"""

# Helpers
from .helpers.guides_helper import Guide_ViewHelper, get_template, enhance_context
from .helpers.age_helper import calculate_age_in_months, calculate_age_range, get_age_appropriate_content, get_next_milestone_age, format_age_display

# Decorators
from .decorators.caching import cache_result, memoize
from .decorators.permissions import (
    ajax_required, staff_or_403, child_owner_required
)

# Middleware
from .middleware.error_handling import ErrorHandler_Middleware
from .middleware.request_logging import RequestLogging_Middleware

__all__ = [
    # Helpers
    'Guide_ViewHelper', 'get_template', 'enhance_context',
    'calculate_age_in_months', 'calculate_age_range',
    'get_age_appropriate_content', 'get_next_milestone_age', 'format_age_display',
    
    # Decorators
    'cache_result', 'memoize',
    'ajax_required', 'staff_or_403', 'child_owner_required',
    
    # Middleware
    'ErrorHandler_Middleware', 'RequestLogging_Middleware'
]