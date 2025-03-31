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
    """Get an item from a dictionary using a key."""
    if dictionary is None or not isinstance(dictionary, dict):
        return 0
    return dictionary.get(key, 0)  # We return 0 if key doesn't exist

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

@register.filter
@stringfilter
def split(value, delimiter):
    """Split the value by the given delimiter."""
    if value:
        return value.split(delimiter)
    return []

@register.filter
@stringfilter
def trim(value):
    """Remove leading and trailing whitespace."""
    if value:
        return value.strip()
    return ""