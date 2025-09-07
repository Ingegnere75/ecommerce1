from django import template
from core.models import HomeBanner

register = template.Library()

@register.inclusion_tag('core/partials/render_banners.html')
def render_banners(posizione):
    banners = HomeBanner.objects.filter(posizione=posizione)
    return {'banners': banners}


