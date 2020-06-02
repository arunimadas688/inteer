from django import template
from django.template import Template,Context
import os.path
from django.contrib.auth.models import User
from adminpanel.models import *
from django.db import connection
from django.db.models import Avg

register = template.Library()
@register.simple_tag
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


@register.simple_tag
def get_logo():
    logo = Logo.objects.get(pk=1)
    return logo


@register.simple_tag
def get_logosocial():
    cursor = connection.cursor()
    cursor.execute("select * from adminpanel_socialmedias where id IN(1,2)")
    socialmedia= dictfetchall(cursor)
    return socialmedia


@register.simple_tag
def get_user(user_id):
 user = User.objects.get(pk=user_id)
 return(user)


@register.simple_tag
def get_userprofile(user_id):
 userprofile = UserProfile.objects.get(user_id=user_id)
 return(userprofile)