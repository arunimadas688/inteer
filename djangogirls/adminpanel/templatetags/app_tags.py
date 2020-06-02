from django import template
import re
TAG_RE = re.compile(r'<[^>]+>')

register = template.Library()

@register.filter(name='strip_tags')
def strip_tags(text):
    return TAG_RE.sub('', text)