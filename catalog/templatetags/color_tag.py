from django import template
from catalog.models import ColorScheme

register = template.Library()
@register.simple_tag
def get_colors():
    print("get_colors called")
    print(ColorScheme.objects.all())
    colors = ColorScheme.objects.all()
    color = ''
    for i in colors:
        color = i
    css = '#hei { background-color: ' + str(color) + ' !important;}'
    return css
