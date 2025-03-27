import re # Regular expressions
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def is_valid_email(email):
    """Check if an email is valid"""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def is_valid_password(password, min_length=8):
    """
    Check if a password is valid:
    - At least min_length characters
    - At least one digit
    - At least one letter
    """
    if len(password) < min_length:
        return False
    
    if not re.search(r'\d', password):  # Digit check
        return False
        
    if not re.search(r'[a-zA-Z]', password):  # Letter check
        return False
        
    return True

def is_valid_url(url):
    """Check if a URL is valid"""
    # We use simple regex for URL validation
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ipv4
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return pattern.match(url) is not None

def contains_special_chars(text):
    """Check if text contains special characters"""
    pattern = re.compile(r'[^a-zA-Z0-9\s]')
    return pattern.search(text) is not None