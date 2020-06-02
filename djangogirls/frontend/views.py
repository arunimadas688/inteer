from django.shortcuts import render
from django.utils import timezone,formats
from django.template import RequestContext,Context, Template, Context, loader
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from adminpanel.models import *
from django.db import connection
from django.db.models import Avg
from datetime import datetime, timedelta
# import PIL
# from PIL import Image
import os
from os.path import basename
from django.conf import settings
from django.db.models import Q
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
#from paypal.standard.forms import PayPalPaymentsForm
#from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from decimal import Decimal

def dictfetchall(cursor):
	"Return all rows from a cursor as a dict"
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]

def home_index(request):
	if 'member_id' in request.session:
		user_id = request.session['member_id']
	cursor = connection.cursor()
	cursor.execute("select * from adminpanel_banner where id=8")
	banner = dictfetchall(cursor)
	cursor.execute("select * from adminpanel_cms where id IN(1,2,3)")
	cms = dictfetchall(cursor)
	cursor.execute("select * from adminpanel_cms where id=5")
	whyinter = dictfetchall(cursor)
	cursor.execute("select * from adminpanel_cms where id IN(6,7,8)")
	bannerlowercms = dictfetchall(cursor)
	return render_to_response('frontend/home.html',{'banner': banner,'cms': cms,'whyinter':whyinter,'bannerlowercms':bannerlowercms})


def login_user(request):
	return render_to_response('frontend/login.html')


def login_user_submit(request):
	if 'member_id' in request.session:
		return HttpResponseRedirect('/dashboard/')
	else:
		msg_error = ""
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				request.session['member_id'] = user.id
				request.session['member_name'] = user.first_name
				request.session['member_email'] = user.email
				return HttpResponseRedirect('/dashboard/')
			else:
				return HttpResponseRedirect('/login/')
		else:
			return HttpResponseRedirect('/login/')


def forgot_password(request):
	return render_to_response('frontend/forgetpassword.html')


def forgot_password_submit(request):
	if request.method == 'POST':
		forgot_mail = request.POST['forgot_mail']
		if User.objects.filter(email=forgot_mail).exists() :
			forgotuser = User.objects.get(email=forgot_mail)
			userprofile = UserProfile.objects.get(user_id=forgotuser.id)
			forgot_link = "http://138.68.12.41:8007/resetpassword/"+str(forgot_mail)
			mailfname = forgotuser.first_name
			forgetpassword_mail=EmailTemplates.objects.get(pk=3)
			t = forgetpassword_mail.templatebody
			t1=t.replace('[NAME]',mailfname,1)
			t2=t1.replace('[LINK]',forgot_link,1)
			msg_html = t2
			send_mail(forgetpassword_mail.subject, 'hello world again', 'tanay@natitsolved.com', [forgotuser.email], html_message=msg_html)
			return HttpResponseRedirect('/login/')
		else :
			msg_error = "Sorry user Not exists!"
			print(msg_error)
			return HttpResponseRedirect('/')
	else :
		return HttpResponseRedirect('/')


def reset_password(request,email):
	user = User.objects.get(email=email)
	return render(request,'frontend/resetpassword.html',{'user': user })


def reset_password_submit(request):
	if 'member_id' not in request.session:
		if request.POST :
			forgot_mail = request.POST['forgot_mail']
			newpassword=request.POST['password']
			confirmpassword=request.POST['cpassword']
			if newpassword != confirmpassword :
				messages.add_message(request, messages.SUCCESS, 'confirmpassword is not same!',fail_silently=True)
				return HttpResponseRedirect('/resetpassword/'+forgot_mail+'/')
			user=User.objects.get(email=forgot_mail)
			user.set_password(newpassword)
			user.save()
			return HttpResponseRedirect('/login')
		else :
		   return HttpResponseRedirect('/')
	else :
		return HttpResponseRedirect('/')

def logout_page(request):
	logout(request)
	return HttpResponseRedirect('/login')


def typeof_signup(request):
	return render_to_response('frontend/signup.html')    


def register_user(request):
	import json
	import base64
	rtn_obj = {}
	if request.method == 'POST':
		if User.objects.filter(email=request.POST['emailaddress']).exists():
			rtn_obj['msg_error'] = "User Exists!"
			data = json.dumps(rtn_obj)
			return render_to_response('frontend/signup.html', {'msg:error':rtn_obj['msg_error']})   
		else :
			import time
			activate_no = int(time.time())
			user = User.objects.create_user(
			password=request.POST['password'],
			is_superuser=False,
			username=request.POST['emailaddress'],
			first_name=request.POST['first_name'],
			last_name=request.POST['last_name'],
			email=request.POST['emailaddress'],
			is_staff=False,
			is_active=False
			)
			user.save()

			#Save userinfo record
			user_info = UserProfile(
			address=request.POST['location'],
			phone_number=request.POST['phonenumber'],
			latitude=request.POST['cityLat'],
			longitude=request.POST['cityLng'],
			is_verified=0,
			interest_id_id=1,
			role_id=2,
			user_id_id=user.id,
			activate_token=activate_no
			)
			user_info.save()

			request.session['member_id'] = user.id
			activation_link = "http://138.68.12.41:8007/activation/"+str(activate_no)
			mailpwd = request.POST['password']
			mailfname = request.POST['first_name']
			register_mail=EmailTemplates.objects.get(pk=1)
			t = register_mail.templatebody
			t1=t.replace('[NAME]',mailfname,1)
			t2=t1.replace('[LINK]',activation_link,1)
			msg_html = t2
			send_mail(register_mail.subject, 'hello world again', 'tanay@natitsolved.com', [user.email], html_message=msg_html)
			rtn_obj['msg_error'] = "Registerd! Please Wait for a momment redirecting.."
			data = json.dumps(rtn_obj)
			return HttpResponseRedirect('/login/')


def activate_link(request,base64string):
	rtnvalue = activate_account(base64string)
	checkval = rtnvalue.split("#")
	if 'member_id' in request.session:
		if checkval[0] == "0":
			messages.add_message(request, messages.SUCCESS, 'Account is already Activated!',fail_silently=True)
			return HttpResponseRedirect('/login/')
		else :
		   messages.add_message(request, messages.SUCCESS, 'Account is Activated!',fail_silently=True)
		   return HttpResponseRedirect('/login/')
	else :
		if checkval[0] == "0":
			messages.add_message(request, messages.SUCCESS, 'Account is already Activated!',fail_silently=True)
			return HttpResponseRedirect('/login/')
		else :
		   request.session['member_id'] = int(checkval[1])
		   messages.add_message(request, messages.SUCCESS, 'Account is Activated!',fail_silently=True)
		   return HttpResponseRedirect('/login/')


def activate_account(base64string):
	if UserProfile.objects.filter(activate_token=int(base64string)).exists():
		profile=UserProfile.objects.get(activate_token=int(base64string))
		user = User.objects.get(pk=profile.user_id_id)
		if user.is_active == True:
		  value_to_rtn = "0"+"#"+str(user.id)
		else :
			user.is_active = True
			user.save()
			value_to_rtn = "1"+"#"+str(user.id)
		return value_to_rtn


def user_profile(request):
	if 'member_id' in request.session:
		user_id = request.session['member_id']
		user = User.objects.filter(pk=user_id).all()
		userprofile = UserProfile.objects.filter(user_id=user_id).all()
		organization = Organization.objects.all()
		coordinatorexists = CordinatorRequest.objects.filter(user_id=user_id).all()
		volunteersexists = Volunteersactivities.objects.filter(user_id=user_id).all()
		interest = Interest.objects.all()
		skill = Skills.objects.all()

		return render(request, 'frontend/profile.html', {'activation_msg': "",'user': user, 'userprofile': userprofile, 'organization': organization, 'req_status': coordinatorexists, 'interest': interest, 'skill': skill, 'volunteersexists' : volunteersexists })
	else :
		return HttpResponseRedirect('/login/')


def profile_edit(request):
	if 'member_id' in request.session:
		user_id = request.session['member_id']
		user = User.objects.get(pk=user_id)
		userprofile = UserProfile.objects.get(user_id=user_id)
		if request.method == 'POST':
			uprofile_update = UserProfile.objects.get(user_id=int(user_id))
			user_edit = User.objects.get(pk=int(user_id))
			user_edit.first_name=request.POST.get('first_name')
			user_edit.last_name=request.POST.get('last_name')
			user_edit.email=request.POST.get('email')
			user_edit.save()
			
			uprofile_update.phone_number=request.POST.get('phone_number')
			uprofile_update.address=request.POST.get('address')
			uprofile_update.physical_ability=request.POST.get('physical_ability')
			uprofile_update.about_me=request.POST.get('about_me')
			uprofile_update.interest_id_id=request.POST.get('interest_id')
			uprofile_update.save()
			messages.add_message(request, messages.SUCCESS, 'Record Updated Successfully!',fail_silently=True)
			return HttpResponseRedirect('/dashboard/')

		return render_to_response('frontend/profile.html',context_instance=RequestContext(request))
	else :
		return HttpResponseRedirect('/login/')


def become_coordinator(request):
	if 'member_id' in request.session:
		org_id_id = request.POST.get('org_id_id')
		org_address = request.POST.get('org_address')
		employee_id = request.POST.get('employee_id')
		if request.POST:
			apply_coordinator = CordinatorRequest(
					user_id_id=request.session['member_id'],
					org_id_id=org_id_id,
					status="Pending",
					address=org_address,
					employee_number=employee_id
					)
			apply_coordinator.save()
			return HttpResponseRedirect('/dashboard/')
		else :
			return HttpResponseRedirect('/dashboard/')
	else :
		return HttpResponseRedirect('/login/')


def becomecoordinator(request):
	if 'member_id' in request.session:
		user_id = request.session['member_id']
		user = User.objects.filter(pk=user_id).all()
		userprofile = UserProfile.objects.filter(user_id=user_id).all()
		organization = Organization.objects.all()
		coordinatorexists = CordinatorRequest.objects.filter(user_id=user_id).all()
		if coordinatorexists:
			for coordinate in coordinatorexists:
				coordinate_data={}
				coordinate_data['status']=coordinate.status
				coordinate_data['org_id']=coordinate.org_id_id
				coordinate_data['org_address']=coordinate.address
				coordinate_data['org_employee_number']=coordinate.employee_number
		else:
			coordinate_data={}
			coordinate_data['status']='notexist'
			coordinate_data['org_id']=''
			coordinate_data['org_address']=''
			coordinate_data['org_employee_number']=''

		interest = Interest.objects.all()
		skill = Skills.objects.all()
		return render(request, 'frontend/becomecoordinator.html', {'activation_msg': "",'user': user, 'userprofile': userprofile, 'organization': organization, 'req_status': coordinate_data, 'interest': interest, 'skill': skill })
	else :
		return HttpResponseRedirect('/login/')
