from django import template
import os.path
from django.contrib.auth.models import User
from adminpanel.models import *
from django.db import connection
register = template.Library()

@register.simple_tag
def get_logo():
    logo = Logo.objects.get(pk=1)
    return logo