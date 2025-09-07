# accounts/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def split(value, delimiter=","):
    """Divide una stringa in una lista usando il delimitatore specificato."""
    if isinstance(value, str):
        return value.split(delimiter)
    return []

@register.filter
def mul(value, arg):
    """Moltiplica due numeri (float x float)."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Moltiplica due valori (compatibile con float e int)."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def classname(obj):
    """Restituisce il nome della classe di un oggetto."""
    return obj.__class__.__name__
