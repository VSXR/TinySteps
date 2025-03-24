# Home views
from .home_views import index, about, page_not_found

# Auth views
from .auth_views import Login_View, Logout_View, Register_View, profile, password_reset

# Contact views
from .contact_views import Contact_View

# Child views 
from .child_views import (
    your_children, your_child, YourChild_Add_View, YourChild_Delete_View, 
    YourChild_UpdateDetails_View, child_milestone, child_calendar, child_vaccine_card,
    YourChild_Calendar_View, YourChild_VaccineCard_View
)

# Forum views
from .forum_views import (
    parents_forum_page, search_posts, view_post, add_post, 
    edit_post, delete_post, add_post_comment, forum_post_like_toggle
)

# Guide views
from .guide_views import (
    guides_page, guide_list_view, guide_detail_view, 
    article_list_view, article_detail_view, my_guides, SubmitGuide_View
)

# Nutrition views
from .nutrition_views import (
    nutrition_analyzer_view, nutrition_comparison_view, nutrition_save_view
)

# Admin views
from .admin_views import (
    review_guides, approve_guide, reject_guide, admin_dashboard
)

# Error views
from .error_views import (
    custom_error_400, custom_error_403, custom_error_404, 
    custom_error_500, database_error_view
)

__all__ = [
    # Home views
    'index', 'about', 'page_not_found',
    
    # Auth views
    'Login_View', 'Logout_View', 'Register_View', 'profile', 'password_reset',

    # Contact views
    'Contact_View',
    
    # Child views
    'your_children', 'your_child', 'YourChild_Add_View', 'YourChild_Delete_View',
    'YourChild_UpdateDetails_View', 'child_milestone', 'child_calendar', 'child_vaccine_card',
    'YourChild_Calendar_View', 'YourChild_VaccineCard_View',
    
    # Forum views
    'parents_forum_page', 'search_posts', 'view_post', 'add_post',
    'edit_post', 'delete_post', 'add_post_comment', 'forum_post_like_toggle',
    
    # Guide views
    'guides_page', 'guide_list_view', 'guide_detail_view',
    'article_list_view', 'article_detail_view', 'my_guides', 'SubmitGuide_View',
    
    # Nutrition views
    'nutrition_analyzer_view', 'nutrition_comparison_view', 'nutrition_save_view',
    
    # Admin views
    'review_guides', 'approve_guide', 'reject_guide', 'admin_dashboard',
    
    # Error views
    'custom_error_400', 'custom_error_403', 'custom_error_404',
    'custom_error_500', 'database_error_view'
]