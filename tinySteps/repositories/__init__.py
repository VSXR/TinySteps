"""Repositories package"""

# Base repository
from .base.base_repository import BaseRepository, GenericRepository

# Child repositories
from .child.child_repository import Child_Repository, CalendarEvent_Repository

# Content repositories
from .content.guide_repository import Guide_Repository
from .content.article_repository import Article_Repository
from .content.forum_repository import Forum_Repository

# User repositories
from .user.user_repository import User_Repository, Profile_Repository

# Nutrition repositories
from .nutrition.nutrition_repository import Nutrition_Repository

# Export commonly used repositories
__all__ = [
    'BaseRepository',
    'GenericRepository',
    'Child_Repository',
    'CalendarEvent_Repository',
    'Guide_Repository',
    'Article_Repository',
    'Forum_Repository',
    'User_Repository',
    'Profile_Repository',
    'Nutrition_Repository',
]