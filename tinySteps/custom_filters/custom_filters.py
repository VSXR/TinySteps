from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags
from django.utils.text import Truncator

register = template.Library()

@register.filter
@stringfilter
def truncate_chars(value, max_length):
    """Truncate a string to the given max_length, adding ellipsis if truncated."""
    return Truncator(value).chars(int(max_length))

@register.filter
@stringfilter
def truncate_words(value, max_words):
    """Truncate a string to the given max number of words, adding ellipsis if truncated."""
    return Truncator(value).words(int(max_words))

@register.filter
@stringfilter
def strip_html(value):
    """Remove HTML tags from a string."""
    return strip_tags(value)

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation in templates."""
    return dictionary.get(key)

@register.filter
def format_age(months):
    """Format age in months to a human-readable string."""
    if not months:
        return ""
    
    years = months // 12
    remaining_months = months % 12
    
    if years > 0 and remaining_months > 0:
        return f"{years}y {remaining_months}m"
    elif years > 0:
        return f"{years}y"
    else:
        return f"{months}m"