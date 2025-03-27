"""Forms package"""

# Authentication forms
from .auth.auth_forms import (
    CustomUserCreation_Form,
    PasswordReset_Form,
)

# Child forms
from .child.core_forms import YourChild_Form
from .child.feature_forms import (
    Milestone_Form,
    Vaccine_Form,
    CalendarEvent_Form,
)

# Communication forms
from .communication.contact_forms import Contact_Form
from .communication.comment_forms import (
    ForumComment_Form,
    GuideComment_Form,
)

# Content forms
from .content.guide_forms import (
    GuideSubmission_Form,
    GuideRejection_Form,
)
from .content.forum_forms import ForumPost_Form

# Export all form classes for backward compatibility
__all__ = [
    # Auth forms
    'CustomUserCreation_Form',
    'PasswordReset_Form',
    
    # Child forms
    'YourChild_Form',
    'Milestone_Form',
    'Vaccine_Form',
    'CalendarEvent_Form',
    
    # Communication forms
    'Contact_Form',
    'ForumComment_Form',
    'GuideComment_Form',
    
    # Content forms
    'GuideSubmission_Form',
    'GuideRejection_Form',
    'ForumPost_Form',
]