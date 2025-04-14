from django import template
from django.utils.html import mark_safe
import re

register = template.Library()

@register.filter
def highlight(text, query):
    if not query or not text:
        return text
    try:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        return mark_safe(pattern.sub(
            lambda m: f'<span class="bg-warning">{m.group(0)}</span>', 
            str(text)
        ))
    except:
        return text