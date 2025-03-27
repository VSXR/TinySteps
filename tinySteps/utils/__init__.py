"""Utils package"""

# Helpers
from .helpers.events import create_event_reminders
from .helpers.views import Guide_ViewHelper
from .helpers.formatting import (
    format_date, truncate_text, slugify, strip_html_tags
)
from .helpers.validation import (
    is_valid_email, is_valid_password, is_valid_url, contains_special_chars
)

# Decorators
from .decorators.caching import cache_result, memoize
from .decorators.permissions import (
    ajax_required, staff_or_403, child_owner_required
)

# Middleware
from .middleware.error_handling import ErrorHandler_Middleware
from .middleware.request_logging import RequestLoggingMiddleware

__all__ = [
    # Helpers
    'create_event_reminders', 'Guide_ViewHelper',
    'format_date', 'truncate_text', 'slugify', 'strip_html_tags',
    'is_valid_email', 'is_valid_password', 'is_valid_url', 'contains_special_chars',
    
    # Decorators
    'cache_result', 'memoize',
    'ajax_required', 'staff_or_403', 'child_owner_required',
    
    # Middleware
    'ErrorHandler_Middleware', 'RequestLoggingMiddleware'
]