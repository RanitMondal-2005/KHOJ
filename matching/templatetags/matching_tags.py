"""
Working of templatetags/matching_tags.py :-
Custom template filters/tags for the matching app.
i.e, These filters are used to determine the visual representation (color and label) of confidence scores in the application.
This is necessary as : it allows for a quick and easy understanding of the confidence levels associated with different matches.
"""

from django import template

register = template.Library()


@register.filter
def confidence_color(score):
    """Return Bootstrap color class based on confidence score."""
    if score >= 80:
        return 'success'
    elif score >= 60:
        return 'warning'
    else:
        return 'secondary'


@register.filter
def confidence_label(score):
    """Return text label based on confidence score."""
    if score >= 80:
        return 'HIGH'
    elif score >= 60:
        return 'MODERATE'
    else:
        return 'LOW'
