from django import template
register = template.Library()

@register.filter
def split_comma(value):
    if not value:
        return []
    return [s.strip() for s in str(value).split(',') if s.strip()]

@register.filter
def get_profile(profiles, user_id):
    for p in profiles:
        if p.user_id == user_id:
            return p
    return None
