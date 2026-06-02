from django import template

register = template.Library()


@register.filter
def status_color(status):
    colors = {
        'CRITICAL': 'danger',
        'WARNING': 'warning',
        'NORMAL': 'success'
    }

    return colors.get(status, 'secondary')


@register.simple_tag
def dashboard_title():
    return "LGU Disaster Early Warning System"