import hashlib
import json
import functools
from django.core.cache import cache

def cache_result(timeout=300):
    """Decorator to cache function results (has a timeout of 5 minutes by default)"""
    def decorator(func):
        """Decorator to cache function results"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper function to cache results"""
            # Create a cache key based on function name and arguments
            key_parts = [func.__name__]
            
            # Add args to key
            for arg in args:
                key_parts.append(str(arg))
                
            # Add kwargs to key (sorted for consistency)
            for k in sorted(kwargs.keys()):
                key_parts.append(f"{k}:{kwargs[k]}")
                
            # We create a hash to use as the cache key
            cache_key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()
            
            # Try to get from cache info for the key
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Not in cache, call the function and store the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def memoize(func):
    """Decorator to memoize function results (cache the result of the function
    so that it is not recalculated if the same arguments are passed again for the 
    purpose of optimization)"""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function to memoize results"""
        # We create a key from the function arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        # Check if result is cached
        if key not in cache:
            # Not cached, call the function
            cache[key] = func(*args, **kwargs)
            
        return cache[key]
    
    # Add a method to clear the cache
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper