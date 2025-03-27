import re
from datetime import datetime
from django.utils.text import slugify as django_slugify

def format_date(date_obj, format_str="%d %b %Y"):
    """Format a date object to a string using the specified format"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    
    return str(date_obj)

def truncate_text(text, max_length=100, ellipsis='...'):
    """Truncate text to max_length and add ellipsis"""
    if not text or len(text) <= max_length:
        return text
    
    # Cut at the last space before max_length to avoid cutting words
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + ellipsis

def slugify(value, max_length=50):
    """Convert text to a URL-friendly slug"""
    slug = django_slugify(value)
    
    # Truncate if needed
    if max_length and len(slug) > max_length:
        slug = slug[:max_length]
    
    return slug

def strip_html_tags(html_text):
    """Remove HTML tags from text"""
    if not html_text:
        return ""
        
    # Simple regex to remove tags
    clean_text = re.sub(r'<[^>]*>', '', html_text)
    return clean_text.strip()