"""Views package"""

# Base Views
from .base.home_views import index, about, page_not_found
from .base.error_views import custom_error_400, custom_error_403, custom_error_404, custom_error_500, database_error_view

# Auth Views
from .auth.auth_views import Login_View, Logout_View, Register_View, profile, password_reset

# Child Views
from .child.core_views import your_children, your_child
from .child.form_views import YourChild_Add_View, YourChild_Delete_View, YourChild_UpdateDetails_View
from .child.feature_views import (
    child_milestone, child_calendar, child_vaccine_card,
    get_child_statistics, growth_status_view,
    YourChild_Calendar_View, YourChild_VaccineCard_View
)

# Forum Views
from .forum.forum_views import (
    parents_forum_page, search_posts, view_post, add_post, 
    edit_post, delete_post, add_post_comment, forum_post_like_toggle
)

# Guide Views
from .guides.guide_views import guides_page, guide_list_view, guide_detail_view, admin_guides_panel_view
from .guides.submission_views import SubmitGuide_View
from .guides.article_views import article_list_view, article_detail_view

# Nutrition Views
from .nutrition.analyzer_views import nutrition_analyzer_view, nutrition_save_view
from .nutrition.comparison_views import nutrition_comparison_view

# Comment Views
from .comments.comment_views import add_comment, delete_comment, list_comments

# Admin Views
from .admin.admin_views import review_guides, approve_guide, reject_guide, admin_dashboard

# Contact Views
from .contact.contact_views import Contact_View

# Policies Views
from .pages.pages_views import terms_view, privacy_view, cookies_view, accessibility_view, help_center_view

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
    'YourChild_Calendar_View', 'YourChild_VaccineCard_View', 'get_child_statistics', 'growth_status_view',

    
    # Forum views
    'parents_forum_page', 'search_posts', 'view_post', 'add_post',
    'edit_post', 'delete_post', 'add_post_comment', 'forum_post_like_toggle',
    
    # Guide views
    'guides_page', 'guide_list_view', 'guide_detail_view', 'admin_guides_panel_view',
    'article_list_view', 'article_detail_view', 'SubmitGuide_View',
    
    # Nutrition views
    'nutrition_analyzer_view', 'nutrition_comparison_view', 'nutrition_save_view',
    
    # Comment views
    'add_comment', 'delete_comment', 'list_comments',

    # Admin views
    'review_guides', 'approve_guide', 'reject_guide', 'admin_dashboard',
    
    # Error views
    'custom_error_400', 'custom_error_403', 'custom_error_404',
    'custom_error_500', 'database_error_view',

    # Policies views
    'terms_view', 'privacy_view', 'cookies_view', 'accessibility_view', 'help_center_view',
]