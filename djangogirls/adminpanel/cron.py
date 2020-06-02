from django.utils import timezone,formats
from django.template import RequestContext, Context, Template
from django.shortcuts import ( 
    render_to_response , 
    render,
    get_object_or_404, 
    reverse
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import *
from django.db import connection
from datetime import datetime , timedelta
import os
from os.path import basename
from django.conf import settings
from django.db.models import Q
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max
from decimal import Decimal
from django.contrib import messages
from django.core.mail import send_mail
import time
from django.urls import reverse
import json
from django.template.loader import render_to_string
from django.conf.urls import include, url
from decimal import*
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def my_scheduled_job():

    current_time  = time.time()
    current_time_before = current_time - 60
    current_time_after = current_time + 60

    current_time_before = str(current_time_before).split('.')[0]
    current_time_after = str(current_time_after).split('.')[0]
    # p=stripe.Subscription.delete("sub_GE2wFSR31Wrkfa")
    # # p = stripe.Subscription.retrieve("sub_GE2wFSR31Wrkfa")
    # print(p)
    # pp = stripe.Event.list(
    #   types=['customer.subscription.updated'],
    #   created={
    #     'gte' : current_time_after,
    #     # 'gte' : 1575633740,
    #     # 'lte' : 1578312140
    #     'lte' : current_time_before
    #   },
    #   limit=100
    # )
    # # print('currenttieme')
    # # print(current_time)
    # if(len(pp['data'])>0):
    #   print(len(pp['data']))
    #   # print(current_time_after)
    #   for updated_subscribed_obj in pp['data']:
    #     sub_id = updated_subscribed_obj['data']['object']['id']
    #     subscription_end_dates = datetime.fromtimestamp(int(updated_subscribed_obj['data']['object']['current_period_end']))

    #     objList  = PayementInformations.objects.filter(subscription_id=sub_id)
    #     userObj = 0
    #     token = 0
    #     plan_type = 0
    #     if len(objList) >= 1:
    #       for obj in objList:
    #         obj.subscription_deleted = 1
    #         obj.subscription_ended = True
    #         obj.save()
    #         userObj = obj.user
    #         token = obj.token
    #         plan_type = obj.plan_type
    #         print('ok')
    #       package = SubscriptionPlanDetails.objects.filter(plan_id = updated_subscribed_obj['data']['object']['plan']['id']).first()
    #       product_response  = stripe.Product.retrieve(updated_subscribed_obj['data']['object']['plan']['product'])
    #       subscription_renew = PayementInformations(
    #         user        = userObj,
    #         userprofile = UserProfile.objects.get(user_id=userObj),
    #         volunteer_number    = updated_subscribed_obj['data']['object']['plan']['transform_usage']['divide_by'],
    #         customer_id  = updated_subscribed_obj['data']['object']['customer'],
    #         email =userObj.email,
    #         token =token,
    #         plan_id =updated_subscribed_obj['data']['object']['plan']['id'],
    #         plan_type = package.plan,
    #         package = package.package,
    #         trial_period =updated_subscribed_obj['data']['object']['plan']['trial_period_days'],
    #         subscription_id = sub_id,
    #         subscription_start_date = updated_subscribed_obj['data']['object']['current_period_start'],
    #         subscription_end_date = updated_subscribed_obj['data']['object']['current_period_end'],
    #         subscribed = True,
    #         subscription_response = updated_subscribed_obj,
    #         plan_response = updated_subscribed_obj['data']['object']['plan'],
    #         product_response = product_response,
    #         subscription_plan_details_id = package
    #       )
    #       subscription_renew.save()

       