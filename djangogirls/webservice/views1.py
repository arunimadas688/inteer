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
import PIL
from PIL import Image
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
import re
#from paypal.standard.forms import PayPalPaymentsForm
#from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from decimal import Decimal
ACCESS_CONTROL_ALLOW_ORIGIN = '*'

def dictfetchall(cursor):
	"Return all rows from a cursor as a dict"
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]

def home_index(request):
	import json
	imageurl="http://138.68.12.41:8007/static/media/"
	cursor = connection.cursor()
	cursor.execute("select banner_image,banner_title,banner_text,banner_logo from adminpanel_banner where id=8")
	banner = dictfetchall(cursor)
	cursor.execute("select banner_image,title,short_description from adminpanel_cms where id IN(1,2,3)")
	cms = dictfetchall(cursor)
	cursor.execute("select banner_image,title,short_description from adminpanel_cms where id=5")
	whyinter = dictfetchall(cursor)
	cursor.execute("select banner_image from adminpanel_cms where id IN(6,7,8)")
	bannerlowercms = dictfetchall(cursor)
	if banner and  cms and  whyinter and  bannerlowercms :
		data = json.dumps({"Ack":"1", "banner":banner,'cms':cms,'whyinter':whyinter,'bannerlowercms':bannerlowercms,'imageurl':imageurl})
		'''HttpResponse.headers.add('Access-Control-Allow-Origin', '*')
		HttpResponse.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
		HttpResponse.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')'''
		return HttpResponse(data)
		'''response.__setitem__("Content-type", "application/json")
		response.__setitem__("Access-Control-Allow-Origin", "*")
		return response'''
		'''return HttpResponse(data)'''
	else:
		data = json.dumps({"Ack":"0", "banner":'','cms':'','whyinter':'','bannerlowercms':'','imageurl':''})
		return HttpResponse(data)

def login_user_submit(request):
	import json
	import base64
	rtn_obj = {}
	if request.method == 'POST':
			username = request.POST.get('username', None)
			password = request.POST.get('password', None)
			#return HttpResponse(username)

			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				request.session['member_id'] = user.id
				userData = User.objects.get(id = user.id)
				userpro = UserProfile.objects.get(user_id = user.id)
				#userrole = UserWithroles.objects.get(user_id=user.id)

				cursor12 = connection.cursor()
				sql2 = "select id, address,subscription_id, phone_number, profile_image, latitude, longitude, about_me, physical_ability, is_verified, interest_id_id from adminpanel_userprofile where user_id_id='"+str(user.id)+"'"
				cursor12.execute(sql2)
				userprofiles = cursor12.fetchone()
				print (userprofiles)
				rtn_obj['ack'] = "1"
				rtn_obj['user_id'] = str(user.id)
				rtn_obj['first_name'] = userData.first_name
				rtn_obj['last_name'] = userData.last_name
				rtn_obj['email'] = userData.email
				# rtn_obj['subscription_id'] = userData.subscription_id
				rtn_obj['username'] = userData.username
			
				#rtn_obj['date_of_birth'] = userpro.year + "-" + userpro.month + "-" + userpro.date
				#rtn_obj['gender'] = userpro.gender
				#rtn_obj['user_image'] = settings.BASE_URL + "/media/profile_image.png/"
				#rtn_obj['urole'] = str(userrole.userroles_id)
				rtn_obj['msg_error'] = " Log In Successfull! "
				#for profile in userprofiles:
				rtn_obj['address'] = userprofiles[1]
				rtn_obj['subscription_id'] = userprofiles[2]
				data = json.dumps(rtn_obj)
				return HttpResponse(data)
			else:
				rtn_obj['ack'] = "0"
				rtn_obj['msg_error'] = " Your username and/or password were incorrect. "
				data = json.dumps(rtn_obj)
				return HttpResponse(data)
	else:
		rtn_obj['ack'] = "2"
		rtn_obj['msg_error'] = "Error 404"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)


def facebook_login(request):
	import json
	rtn_obj = {}

	# if 'member_id' in request.session:
	#    return HttpResponse('0') # already logged in
	# else:
	if request.method == 'POST':
		fbid = request.POST['fbid']
		fname = request.POST['first_name']
		lname = request.POST['last_name']
		username = request.POST['username']
		email = request.POST['email']
		if User.objects.filter(email=email).exists():
			UserData = User.objects.get(email=email)
			fbprofile = UserProfile.objects.get(user_id = UserData.id)
			fbprofile.facebook_id = fbid
			fbprofile.save()
			rtn_obj['ack'] = "1"
			rtn_obj['user_id'] = str(UserData.id)
			rtn_obj['first_name'] = fname
			rtn_obj['last_name'] = lname
			rtn_obj['email'] = email
			rtn_obj['fb_id'] = fbid
			rtn_obj['msg_error'] = " Log In Successfull! "
			data = json.dumps(rtn_obj)
			return HttpResponse(data)

		else :
			if UserProfile.objects.filter(facebook_id=fbid).exists():
				fbprofile = UserProfile.objects.get(facebook_id=fbid)
				UserData = User.objects.get(email=email)
				# request.session['member_id'] = fbprofile.user_id
				rtn_obj['ack'] = "1"
				rtn_obj['user_id'] = str(UserData.id)
				rtn_obj['first_name'] = fname
				rtn_obj['last_name'] = lname
				rtn_obj['email'] = email
				rtn_obj['fb_id'] = fbid
				rtn_obj['msg_error'] = " Log In Successfull! "
				data = json.dumps(rtn_obj)
				return HttpResponse(data)
			else :
				user = User.objects.create_user(
					username = username,
					email = email,
					first_name = fname,
					last_name = lname
				)
				user.save()

				userID = user.id

				new_profile = UserProfile(
					user = user,
					facebook_id = fbid
				)
				new_profile.save()
				user_withroles = UserWithroles(
					user = user,
					userroles_id = 2
				)
				user_withroles.save()

				# request.session['member_id'] = user.id
				rtn_obj['ack'] = "1"
				rtn_obj['user_id'] = str(userID)
				rtn_obj['first_name'] = fname
				rtn_obj['last_name'] = lname
				rtn_obj['email'] = email
				rtn_obj['fb_id'] = fbid
				rtn_obj['msg_error'] = " Log In Successfull! "
				data = json.dumps(rtn_obj)
				return HttpResponse(data)


def google_login(request):
	import json
	rtn_obj = {}

	# if 'member_id' in request.session:
	#    return HttpResponse('0') # already logged in
	# else:
	if request.method == 'POST':
		gpid = request.POST['gpid']
		fname = request.POST['first_name']
		lname = request.POST['last_name']
		username = request.POST['username']
		email = request.POST['email']
		if User.objects.filter(email = email).exists():
			UserData = User.objects.get(email=email)
			fbprofile = UserProfile.objects.get(user_id = UserData.id)
			fbprofile.google_id = gpid
			fbprofile.save()
			rtn_obj['ack'] = "1"
			rtn_obj['user_id'] = str(UserData.id)
			rtn_obj['first_name'] = fname
			rtn_obj['last_name'] = lname
			rtn_obj['email'] = email
			rtn_obj['gp_id'] = gpid
			rtn_obj['msg_error'] = " Log In Successfull! "
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
		else :
			if UserProfile.objects.filter(google_id = gpid).exists():
				fbprofile = UserProfile.objects.get(google_id = gpid)
				UserData = User.objects.get(email=email)
				# request.session['member_id'] = fbprofile.user_id
				rtn_obj['ack'] = "1"
				rtn_obj['user_id'] = str(UserData.id)
				rtn_obj['first_name'] = fname
				rtn_obj['last_name'] = lname
				rtn_obj['email'] = email
				rtn_obj['gp_id'] = gpid
				rtn_obj['msg_error'] = " Log In Successfull! "
				data = json.dumps(rtn_obj)
				return HttpResponse(data)
			else :
				user = User.objects.create_user(
					username = username,
					email = email,
					first_name = fname,
					last_name = lname
				)
				user.save()

				userID = user.id

				new_profile = UserProfile(
					user = user,
					google_id = gpid
				)
				new_profile.save()
				user_withroles = UserWithroles(
					user = user,
					userroles_id = 2
				)
				user_withroles.save()

				# request.session['member_id'] = user.id
				rtn_obj['ack'] = "1"
				rtn_obj['user_id'] = str(userID)
				rtn_obj['first_name'] = fname
				rtn_obj['last_name'] = lname
				rtn_obj['email'] = email
				rtn_obj['gp_id'] = gpid
				rtn_obj['msg_error'] = " Log In Successfull! "
				data = json.dumps(rtn_obj)
				return HttpResponse(data)

def forgot_password_submit(request):
	import json
	rtn_obj = {}
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
			rtn_obj['ack'] = "1"
			rtn_obj['msg_error'] = "Email Send successfully"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
		else :
			rtn_obj['ack'] = "0"
			rtn_obj['msg_error'] = "Email not Send successfully"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
	else :
		rtn_obj['ack'] = "0"
		rtn_obj['msg_error'] = "Email not Send successfully"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)


def reset_password_submit(request):
	import json
	rtn_obj = {}
	if request.POST :
		forgot_mail = request.POST['forgot_mail']
		newpassword=request.POST['password']
		confirmpassword=request.POST['cpassword']
		if newpassword != confirmpassword :
			rtn_obj['ack'] = "0"
			rtn_obj['msg_error'] = "confirmpassword is not same!"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
		else :
			user=User.objects.get(email=forgot_mail)
			user.set_password(newpassword)
			user.save()
			rtn_obj['ack'] = "1"
			rtn_obj['msg_error'] = "Password change successfully"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
	else :
			rtn_obj['ack'] = "0"
			rtn_obj['msg_error'] = "Password Not change successfully"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)


def logout_page(request):
	import json
	rtn_obj = {}
	logout(request)
	rtn_obj['ack'] = "1"
	rtn_obj['msg_error'] = "Logout Successfully"
	data = json.dumps(rtn_obj)
	return HttpResponse(data)


def register_user(request):
	import json
	import base64
	rtn_obj = {}
	first_name = request.POST.get('first_name', None)
	last_name = request.POST.get('last_name', None)
	email = request.POST.get('email', None)
	location = request.POST.get('location', None)
	phonenumber = request.POST.get('phonenumber', None)
	cityLat = request.POST.get('cityLat', None)
	cityLng = request.POST.get('cityLng', None)
	password = request.POST.get('password', None)

	if request.method == 'POST':
		if User.objects.filter(email=email).exists():
			rtn_obj['msg_error'] = "User Exists!"
			rtn_obj['ack'] = "0"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
		else :
			import time
			activate_no = int(time.time())
			user = User.objects.create_user(
			password=password,
			is_superuser=False,
			username=email,
			first_name=first_name,
			last_name=last_name,
			email=email,
			is_staff=False,
			is_active=True
			)
			user.save()

			#Save userinfo record
			user_info = UserProfile(
			address=location,
			phone_number=phonenumber,
			latitude=cityLat,
			longitude=cityLng,
			is_verified=0,
			interest_id_id=1,
			role_id=2,
			user_id_id=user.id,
			activate_token=activate_no
			)
			user_info.save()

			#request.session['member_id'] = user.id
			#activation_link = "http://111.93.169.90/team4/inteerApp/activation/"+str(activate_no)
			activation_link = "http://138.68.12.41:8007/api/activation/"+str(activate_no)
			mailpwd = request.POST.get('password', None)
			mailfname = request.POST.get('first_name', None)
			register_mail=EmailTemplates.objects.get(pk=1)
			t = register_mail.templatebody
			t1=t.replace('[NAME]',mailfname,1)
			t2=t1.replace('[LINK]',activation_link,1)
			msg_html = t2
			send_mail(register_mail.subject, 'InterApp', 'tanay@natitsolved.com', [user.email], html_message=msg_html)
			rtn_obj['msg_error'] = "Registerd!"
			rtn_obj['ack'] = "1"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
	else :
		rtn_obj['msg_error'] = "Registerd Not Successful!"
		rtn_obj['ack'] = "2"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)


def activate_link(request,base64string):
	#return HttpResponse(base64string)
	import json
	import base64
	rtn_obj = {}
	rtnvalue = activate_account(base64string)
	#checkval = rtnvalue.split("#")
	#if checkval[0] == "0":
	if rtnvalue == "0":
	   #messages.add_message(request, messages.SUCCESS, 'Account is already Activated!',fail_silently=True)
		rtn_obj['msg_error'] = "Account is already Activated!"
		rtn_obj['Ack'] = "0"
		data = json.dumps(rtn_obj)
		return HttpResponseRedirect("http://111.93.169.90/team4/inteerApp/#/login")
		#return HttpResponse(data)
	else :
		   #messages.add_message(request, messages.SUCCESS, 'Account is Activated!',fail_silently=True)
		   rtn_obj['msg_error'] = "Account is Activated!"
		   rtn_obj['Ack'] = "1"
		   data = json.dumps(rtn_obj)
		   return HttpResponseRedirect("http://111.93.169.90/team4/inteerApp/#/login")
		   #return redirect("http://111.93.169.90/team4/inteerApp/#/login")
		   #return HttpResponse(data)


def activate_account(base64string):
	if UserProfile.objects.filter(activate_token=int(base64string)).exists():
		profile=UserProfile.objects.get(activate_token=int(base64string))
		user = User.objects.get(pk=profile.user_id_id)
		#if user.is_active == True:
		  #value_to_rtn = "0"+"#"+str(user.id)
		#else :
		user.is_active = True
		user.save()
		value_to_rtn = "1"
		#value_to_rtn = "1"+"#"+str(user.id)
		return value_to_rtn


def user_profile(request):
	import json
	rtn_obj = {}
	imageurl="http://138.68.12.41:8007/static/media/"
	if request.method == 'POST':
		user_id = request.POST.get('user_id',None)
		#user = User.objects.get(pk=user_id)
		#return HttpResponse(user_id)
		cursor11 = connection.cursor()
		sql1 = "select id,email,first_name,last_name from auth_user where id='"+user_id+"'"
		cursor11.execute(sql1)
		user = cursor11.fetchone()

		#userprofile = UserProfile.objects.get(user_id_id=user_id)

		cursor12 = connection.cursor()
		sql2 = "select id, address, phone_number, profile_image, latitude, longitude, about_me, physical_ability, is_verified, interest_id_id from adminpanel_userprofile where user_id_id='"+user_id+"'"
		cursor12.execute(sql2)
		userprofiles = cursor12.fetchone()
		#return HttpResponse(userprofiles)

		#organization = Organization.objects.all()
		#coordinatorexists = CordinatorRequest.objects.get(user_id=user_id)
		cursor13 = connection.cursor()
		sql3 = "select adminpanel_cordinatorrequest.*,adminpanel_cordinatorrequest.id as cid, adminpanel_cordinatorrequest.org_id_id as org_id, adminpanel_cordinatorrequest.user_id_id as user_id, adminpanel_organization.*, adminpanel_organization.id as org_id, adminpanel_organization.organization_name as org_name, adminpanel_organization.address as address from adminpanel_cordinatorrequest inner join adminpanel_organization on adminpanel_cordinatorrequest.org_id_id=adminpanel_organization.id where adminpanel_cordinatorrequest.user_id_id='"+user_id+"' and adminpanel_cordinatorrequest.status='Approved'"
		cursor13.execute(sql3)
		coordinatorexist = dictfetchall(cursor13)

		#interest = Interest.objects.all()
		#skill = Skills.objects.all()

		if user and  userprofiles and  coordinatorexist :
			data = json.dumps({"Ack":"1", "user_id":user_id,'user':user,'userprofile':userprofiles,'organization':'','coordinatorexists':coordinatorexist,'interest':'','skill':'','imageurl':imageurl})
			#return HttpResponse(data)
			'''response = HttpResponse(data)
			response.__setitem__("Content-type", "application/json")
			response.__setitem__("Access-Control-Allow-Origin", "*")
			return response'''
			return HttpResponse(data)
		else:
		   data = json.dumps({"Ack":"0", "user_id":user_id,'user':user,'userprofile':userprofiles,'organization':'','coordinatorexists':'','interest':'','skill':'','imageurl':''})
		   return HttpResponse(data)
	else :
		 data = json.dumps({"Ack":"0", "user_id":'','user':'','userprofile':'','organization':'','coordinatorexists':'','interest':'','skill':'','imageurl':''})
		 return HttpResponse(data)

def profile_edit(request):
	import json
	rtn_obj = {}
	if request.method == 'POST':
		user_id = request.POST.get('user_id',None)
		email = request.POST.get('email',None)
		first_name = request.POST.get('first_name',None)
		last_name = request.POST.get('last_name',None)
		phone_number = request.POST.get('phone_number',None)
		if request.method == 'POST':
			cursor1 = connection.cursor()
			cursor1.execute("update auth_user SET first_name='"+first_name+"', last_name='"+last_name+"', email='"+email+"' WHERE id='"+user_id+"'")
			cursor2 = connection.cursor()
			cursor2.execute("update adminpanel_userprofile SET phone_number='"+phone_number+"' WHERE user_id_id='"+user_id+"'")
			rtn_obj['msg_error'] = "Profile Updated successfully!"
			rtn_obj['Ack'] = "1"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
		else :
			rtn_obj['msg_error'] = "Profile not Updated successfully!"
			rtn_obj['Ack'] = "0"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
	else :
		rtn_obj['msg_error'] = "Profile not Updated successfully!"
		rtn_obj['Ack'] = "0"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)

def become_coordinator(request):
	import json
	rtn_obj = {}
	if request.method == 'POST':
		org_id_id = request.POST.get('org_id',None)
		org_address = request.POST.get('org_address',None)
		employee_id = request.POST.get('employee_id',None)
		role = request.POST.get('role',None)
		opp_id = request.POST.get('opp_id',None)
		# org_id_id = request.POST['org_id_id']
		# org_address = request.POST['org_address']
		# employee_id = request.POST['employee_id']
		if request.POST:
			apply_coordinator = CordinatorRequest(
					user_id_id= request.POST.get('user_id',None),
					org_id_id=org_id_id,
					status="Pending",
					address=org_address,
					employee_number=employee_id,
					oppurtunity_id=opp_id,
					role=role
					)
			apply_coordinator.save()
			rtn_obj['msg_error'] = "Your application submited successfully!"
			rtn_obj['Ack'] = "1"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
		else :
			rtn_obj['msg_error'] = "Your application not submited successfully!"
			rtn_obj['Ack'] = "0"
			data = json.dumps(rtn_obj)
			return HttpResponse(data)
	else :
		rtn_obj['msg_error'] = "Your application not submited successfully!"
		rtn_obj['Ack'] = "0"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)


def becomecoordinator(request):
	import json
	rtn_obj = {}
	imageurl="http://138.68.12.41:8007/static/media/"
	if request.method == 'POST':
		#user_id =request.POST['user_id']
		user_id = request.POST.get('user_id',None)
		# user = User.objects.filter(pk=user_id).all()
		# userprofile = UserProfile.objects.filter(user_id=user_id).all()
		# organization = Organization.objects.all()
		# coordinatorexists = CordinatorRequest.objects.filter(user_id=user_id).all()

		cursor11 = connection.cursor()
		sql1 = "select id,email,first_name,last_name from auth_user where id='"+user_id+"'"
		cursor11.execute(sql1)
		user = cursor11.fetchone()

		#userprofile = UserProfile.objects.get(user_id_id=user_id)

		cursor12 = connection.cursor()
		sql2 = "select id, address, phone_number, profile_image, latitude, longitude, about_me, physical_ability, is_verified, interest_id_id from adminpanel_userprofile where user_id_id='"+user_id+"'"
		cursor12.execute(sql2)
		userprofiles = cursor12.fetchone()
		#return HttpResponse(userprofiles)

		cursor14 = connection.cursor()
		sql4 = "select * from adminpanel_organization"
		cursor14.execute(sql4)
		organization = dictfetchall(cursor14)


		#coordinatorexists = CordinatorRequest.objects.get(user_id=user_id)
		cursor13 = connection.cursor()
		sql3 = "select adminpanel_cordinatorrequest.*,adminpanel_cordinatorrequest.id as cid, adminpanel_cordinatorrequest.org_id_id as org_id, adminpanel_cordinatorrequest.user_id_id as user_id, adminpanel_cordinatorrequest.address as caddress, adminpanel_organization.*, adminpanel_organization.id as org_id, adminpanel_organization.organization_name as org_name from adminpanel_cordinatorrequest inner join adminpanel_organization on adminpanel_cordinatorrequest.org_id_id=adminpanel_organization.id where adminpanel_cordinatorrequest.user_id_id='"+user_id+"'"
		cursor13.execute(sql3)
		coordinatorexists = dictfetchall(cursor13)


		if coordinatorexists:
			for coordinate in coordinatorexists:
				coordinate_data={}
				coordinate_data['status']=coordinate['status']
				coordinate_data['org_id']=coordinate['org_id_id']
				coordinate_data['org_address']=coordinate['caddress']
				coordinate_data['org_employee_number']=coordinate['employee_number']
		else:
			coordinate_data={}
			coordinate_data['status']='notexist'
			coordinate_data['org_id']=''
			coordinate_data['org_address']=''
			coordinate_data['org_employee_number']=''

		#interest = Interest.objects.all()
		#skill = Skills.objects.all()
		#if user and  userprofiles and coordinatorexists :
		data = json.dumps({"Ack":"1", "user_id":user_id,'user':user,'userprofile':userprofiles,'coordinatorexists':coordinatorexists,'imageurl':imageurl,'coordinate_data':coordinate_data,'organization':organization})
		return HttpResponse(data)
		#else:
		   #data = json.dumps({"Ack":"2", "user_id":user_id,'user':user,'userprofile':userprofiles,'coordinatorexists':'','imageurl':'','coordinate_data':'','organization':organization})
		   #return HttpResponse(data)
	else :
		 data = json.dumps({"Ack":"0", "user_id":'','user':'','userprofile':'','organization':'','coordinatorexists':'','interest':'','skill':'','imageurl':'','coordinate_data':''})
		 return HttpResponse(data)


def change_password(request):
	import json

	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		new_password = request.POST.get('new_password', None)
		conf_password = request.POST.get('conf_password', None)

		if new_password == conf_password:
			u = User.objects.get(id=user_id)
			u.set_password(new_password)
			u.save()

			data = json.dumps({"Ack": 1, "msg": "Password successfully changed"})
		else:
			data = json.dumps({"Ack": 0, "msg": "Password and confirm password not matched"})
		return HttpResponse(data)


def get_activity_categories(self):
	import json

	cursor13 = connection.cursor()
	sql3 = "select * from adminpanel_activitycategory"
	cursor13.execute(sql3)
	categories = dictfetchall(cursor13)

	data = json.dumps({"Ack": 1, "categories": categories})

	return HttpResponse(data)

def get_organizations(self):
	import json

	cursor14 = connection.cursor()
	sql4 = "select * from adminpanel_organization"
	cursor14.execute(sql4)
	organizations = dictfetchall(cursor14)
	data = json.dumps({"Ack": 1, "organizations": organizations})
	return HttpResponse(data)

def get_opportunity_by_user(request):
	import json

	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		cursor = connection.cursor()
		sql = "select id, opportunity_name from adminpanel_opportunities WHERE user_id_id=" + user_id
		cursor.execute(sql)
		opportunities = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "opportunities": opportunities})
	return HttpResponse(data)

def add_activity_category(request):
	import json

	if request.method == 'POST':
		name = request.POST.get('name', None)
		desc = request.POST.get('description', None)

		activity_category = ActivityCategory(
			name = name,
			description = desc
		)
		activity_category.save()

		data = json.dumps({"Ack": 1, "msg": "Activity category successfully saved"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

def add_opportunity(request):
	import json

	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		org_id = request.POST.get('org_id', None)
		opportunity_name = request.POST.get('opportunity_name', None)
		description = request.POST.get('description', None)
		no_of_volunteers = request.POST.get('no_of_volunteers', None)
		author_name = request.POST.get('author_name', None)
		address = request.POST.get('address', None)

		category_ids = request.POST.get('category_id')
		category_ids = json.loads(category_ids)

		reminders = request.POST.get('reminders')
		reminders = json.loads(reminders)

		parent_id = request.POST.get('parent_id', None)
		no_ofyear = request.POST.get('no_ofyear', None)
		start_date = request.POST.get('start_date', None)
		end_date = request.POST.get('end_date', None)
		questions = request.POST.get('questions')
		questions = json.loads(questions)

		# print(questions)
		# return HttpResponse(1)
		
		if len(request.FILES) != 0:
			image_file = request.FILES['file']
		else :
			image_file = ''

		# volunteer_id = request.POST.get('volunteer_id', None)
		# is_valid = request.POST.get('is_valid', None)
		# is_public = request.POST.get('is_public', None)
		# is_recurring = request.POST.get('is_recurring', None)
		# parent_opportunity = request.POST.get('parent_opportunity', None)


		cursor = connection.cursor()
		sql = "select * from adminpanel_cordinatorrequest where user_id_id='"+ user_id +"'"
		cursor.execute(sql)
		getorgId = dictfetchall(cursor)

		org_id_id = getorgId[0]['org_id_id']

		user = User.objects.get(id=user_id)
		organization = Organization.objects.get(id = org_id_id)
		# category = ActivityCategory.objects.get(id = category_id)
		# volunteer = Volunteer.objects.get(id = volunteer_id)

		opportunitiy = Opportunities(
			user_id = user,
			org_id = organization,
			opportunity_name = opportunity_name,
			description = description,
			author_name = author_name,
			address = address,
			# category_id = category,
			parent_id = 0,
			# is_valid = 1,
			# is_public = 1,
			# is_recurring = 0,
			no_ofyear = no_ofyear,
			parent_opportunity = 0,
			start_date = start_date,
			end_date = end_date,
			image = image_file
		)

		opportunitiy.save()

		if image_file:
			imgthumb = Image.open(settings.MEDIA_ROOT+"/"+opportunitiy.image.name)
			imgthumb.save(settings.MEDIA_ROOT + '/' + opportunitiy.image.name)
			opportunitiy.image = opportunitiy.image.name
			opportunitiy.save()

		opportunityObj = Opportunities.objects.latest('id')

		for cat in category_ids:
			catObj = ActivityCategory.objects.get(id = cat['id'])
			opportunityCategories = OpportunityCategories(
				opportunity_id = opportunityObj,
				category_id = catObj
			)
			opportunityCategories.save()

		for reminder in reminders:
			rem = Reminders(
				start_date = reminder['date'],
				before_hour = reminder['hour'],
				opportunity_id = opportunityObj
			)
			rem.save()

		for question in questions:
			question = OpportunityQuestions(
				opportunity = opportunityObj,
				question = question['question']
			)
			question.save()

		data = json.dumps({"Ack": 1, "msg": "Opportunity successfully saved"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})

	return HttpResponse(data)


def add_organiztion(request):
	import json

	if request.method == 'POST':
		organization_name = request.POST.get('organization_name', None)
		parent_id = request.POST.get('parent_id', None)
		address = request.POST.get('address', None)
		tax_id = request.POST.get('tax_id', None)
		email = request.POST.get('email', None)
		web_url = request.POST.get('web_url', None)
		phone = request.POST.get('phone', None)
		cause = request.POST.get('cause', None)
		about_us = request.POST.get('about_us', None)
		our_activity = request.POST.get('our_activity', None)
		why_us = request.POST.get('why_us', None)
		photo =request.POST.get('photo', None)

		organization = Organization(
			organization_name = organization_name,
			parent_id = parent_id,
			address = address,
			tax_id = tax_id,
			email = email,
			web_url = web_url,
			phone = phone,
			cause = cause,
			about_us = about_us,
			our_activity = our_activity,
			why_us = why_us,
			photo = photo
		)

		organization.save()

		data = json.dumps({"Ack": 1, "msg": "Organization successfully saved"})

	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)


def add_volunteer(request):
	import json

	if request.method == 'POST':
		volunteer_name = request.POST.get('volunteer_name')
		volunteer = Volunteer(
			volunteer_name = volunteer_name
		)
		volunteer.save()
		data = json.dumps({"Ack": 1, "msg": "Volunteer Added"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

def get_volunteers(request):
	import json

	if request.method == 'GET':
		cursor = connection.cursor()
		sql = "select * from adminpanel_volunteer"
		cursor.execute(sql)
		volunteers = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "volunteers": volunteers})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

def get_opportunities(self):
	import json

	cursor = connection.cursor()
	sql = """select AO.id, AO.opportunity_name, AO.description, AO.image, AU.first_name, AU.last_name, AO.org_id_id 
				from adminpanel_opportunities AO
				left join auth_user AU
				on AO.user_id_id = AU.id 
				order by AO.id desc"""
	cursor.execute(sql)
	opportunities = dictfetchall(cursor)
	data = json.dumps({"Ack": 1, "opportunities": opportunities, "image_url": settings.BASE_URL + "/media/"})
	return HttpResponse(data)

def get_opportunitiesfiltered(request):
	import json

	if request.method == 'POST':
		name = request.POST.get('name', None)
		cat_ids = request.POST.get('categories', None)
		cat_ids = json.loads(cat_ids)
		ids = ",".join(str(x) for x in cat_ids)

		c = connection.cursor()
		sql = "SELECT AO.id, AO.opportunity_name, AO.description, AO.image, AU.id uid, AU.first_name, AU.last_name "
		sql += "FROM adminpanel_opportunities AO "
		sql += "LEFT JOIN auth_user AU "
		sql += "ON AO.user_id_id = AU.id "
		sql += "LEFT JOIN adminpanel_opportunitycategories AOC "
		sql += "ON AOC.opportunity_id_id = AO.id "
		sql += "LEFT JOIN adminpanel_activitycategory AAC "
		sql += "ON AAC.id = AOC.category_id_id "
		sql += "WHERE 1=1 "

		if name:
			sql += "AND AO.opportunity_name LIKE '%"+name+"%' "

		if ids:
			sql += "AND AOC.category_id_id IN ("+ids+") "

		sql += "GROUP BY AO.id, uid"

		c.execute(sql)
		allRow = dictfetchall(c)

		data = json.dumps({"Ack": 1, "opportunities": allRow})
	else :
		data = json.dumps({"Ack": 0, "msg": "Only POST method allowed"})
	return HttpResponse(data)


	# cursor = connection.cursor()
	# sql = """select AO.id, AO.interest_id, AO.opportunity_name, AU.first_name, AU.last_name
	# 			from adminpanel_opportunities AO
	# 			left join auth_user AU
	# 			on AO.user_id_id = AU.id"""
	# cursor.execute(sql)
	# opportunities = dictfetchall(cursor)

	# for coordinate in opportunities:
	# 	opportunities_data={}
	# 	#opportunities_data['bool']= bool(str(coordinate['id']) in request.POST.get('interestid', None))
	# 	if bool(str(coordinate['interest_id']) in request.POST.get('interestid', None)):
	# 		opportunities_data['id']=coordinate['id']
	# 		opportunities_data['first_name']=coordinate['first_name']
	# 		opportunities_data['last_name']=coordinate['last_name']
	# 		opportunities_data['opportunity_name']=coordinate['opportunity_name']
	# 		dataTT.append(opportunities_data)

def get_opportunity_by_id(request):
	import json
	from datetime import datetime
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		id = request.POST.get('id', None)
		user_id = request.POST.get('user_id', None)

		cursor = connection.cursor()
		sql = "select ao.id,ao.user_id_id,ao.opportunity_name, ao.org_id_id, ao.description, ao.address, ao.image,ao.no_of_volunteers, au.first_name, au.last_name from adminpanel_opportunities ao left join auth_user au on ao.user_id_id = au.id WHERE ao.id="+id
		# sql = "select ao.*, au.first_name, au.last_name from adminpanel_opportunities ao left join auth_user au on ao.user_id_id = au.id WHERE ao.id="+id
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		# created_date=opportunity[0]['start_date']
		# dt2 = created_date.split(' ')
		# finalconvertedDate=datetime.strptime(dt2[0],'%Y-%m-%d').date()
		# opportunity[0]['start_date']=finalconvertedDate;		
		c = connection.cursor()
		
		catSql = "SELECT aac.id, aac.name, aac.description, aac.category_image FROM adminpanel_opportunitycategories aoc LEFT JOIN adminpanel_activitycategory aac ON aac.id = aoc.category_id_id WHERE aoc.opportunity_id_id = '"+ id +"'"
		c.execute(catSql)
		cats = dictfetchall(c)

		orgid = str(opportunity[0]['org_id_id'])

		organization_cursor = connection.cursor()
		organization_sql = "select * from adminpanel_organization WHERE id='"+ orgid +"'"
		organization_cursor.execute(organization_sql)
		organization = dictfetchall(organization_cursor)

		# org_name = organization[0]['organization_name'] 

		question_cursor = connection.cursor()
		question_sql = "select * from adminpanel_opportunityquestions where opportunity_id ="+id
		question_cursor.execute(question_sql)
		questions = dictfetchall(question_cursor)

		applied = {"status": ""}
		saved = False

		if user_id != None:
			conn = connection.cursor()
			check_sql = "select * from adminpanel_cordinatorrequest where user_id_id = " + user_id + " and oppurtunity_id = " + id
			conn.execute(check_sql)
			user_objs = dictfetchall(conn)
			if len(user_objs) > 0:
				applied['status'] = user_objs[0]['status']

			conn1 = connection.cursor()
			check_saved_sql = "select count(id) from adminpanel_opportunitysaved where user_id = " + user_id + " AND opportunity_id = " + id
			conn1.execute(check_saved_sql)
			check_objs = dictfetchall(conn1)
			if check_objs[0]['count'] == 1:
				saved = True
			
		reminder_conn = connection.cursor()
		reminders_sql = "select id, start_date as date, before_hour as hour from adminpanel_reminders where opportunity_id_id = " + id
		reminder_conn.execute(reminders_sql)
		reminders = dictfetchall(reminder_conn)

		data = json.dumps({"Ack": 1,"organization":organization, "opportunity": opportunity, "image_url": settings.BASE_URL + "/media/", "cats": cats, "questions": questions, "applied": applied, "saved": saved, "reminders": reminders})
	return HttpResponse(data)

def submit_volenteer_request(request):
	import json
	if request.method == 'POST':
		id = request.POST.get('id', None)
		user_id = request.POST.get('user_id', None)
		role = request.POST.get('role',None)
		c = connection.cursor()
		catSql = "SELECT * FROM adminpanel_opportunities WHERE id="+id
		c.execute(catSql)
		cats = dictfetchall(c)
		getorgId=cats[0]['org_id_id']
		apply_coordinator = CordinatorRequest(
			user_id_id=user_id,
			org_id_id=getorgId,
			status="Pending",
			address='N/A',
			employee_number=0,
			oppurtunity_id=id,
			role=role
			)
		apply_coordinator.save()
		data = json.dumps({"Ack": 1, "msg": "Volunteer Applied"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

def interest(request):
	import json
	layoutdata = {}
	homepagelayout = {}
	dataLL = {}
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM adminpanel_interest")
	homelayouts = dictfetchall(cursor)
	dataF = json.dumps(homelayouts)
	return HttpResponse(dataF)

def detail(request):
	message = 'hello';
	return HttpResponse(message)

def detailjson(request):
	import json
	dataF = json.dumps({"Ack": 1})
	return HttpResponse(dataF)


def get_opportunity_by_user_date(request):
	import json
	import datetime
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		event_date = request.POST.get('event_date', None)
		cursor = connection.cursor()
		sql = "select id, opportunity_name from adminpanel_opportunities WHERE user_id_id="+user_id+ " and date(start_date)='"+ event_date +"'"
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "opportunities": opportunity})
	return HttpResponse(data)


def add_activity(request):
	import json
	activity_name = request.POST.get('activity_name', None)
	description = request.POST.get('description', None)
	start_date = request.POST.get('start_date', None)
	end_date = request.POST.get('end_date', None)
	opportunity_id = request.POST.get('opportunity_id', None)

	# if len(request.FILES) != 0:
	#     image = request.FILES['file']
	# else :
	#     image = ''

	activities = Activities(
		opportunity = Opportunities.objects.get(id = opportunity_id),
		activity_name = activity_name,
		author_name = '',
		address = '',
		start_date = start_date,
		end_date = end_date,
		description = description
	)
	activities.save()
	data = json.dumps({"Ack": 1, "msg": "Activity successfully saved"})
	return HttpResponse(data)

def edit_activity(request):
	import json
	id = request.POST.get('id', None)
	activity_name = request.POST.get('activity_name', None)
	description = request.POST.get('description', None)
	start_date = request.POST.get('start_date', None)
	end_date = request.POST.get('end_date', None)

	cursor1 = connection.cursor()
	cursor1.execute("update adminpanel_activities SET activity_name='"+activity_name+"', description='"+description+"', start_date='"+start_date+"', end_date='"+end_date+"' WHERE id='"+id+"'")
	
	data = json.dumps({"Ack": 1, "msg": "Activity updated successfully"})
	return HttpResponse(data)

	

def get_activities(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder

	if request.method == 'POST':
		opportunity_id = request.POST.get('opportunity_id', None)

		cursor = connection.cursor()
		sql = "SELECT * FROM adminpanel_activities WHERE opportunity_id="+opportunity_id
		cursor.execute(sql)
		activities = dictfetchall(cursor)

		data = json.dumps({"Ack": 1, "activities": activities}, cls=DjangoJSONEncoder)
	else :
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def get_activity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder

	if request.method == 'POST':
		activity_id = request.POST.get('activity_id', None)

		cursor = connection.cursor()
		sql = "SELECT * FROM adminpanel_activities WHERE id="+str(activity_id)
		cursor.execute(sql)
		activities = dictfetchall(cursor)

		created_date = str(activities[0]['start_date'])
		dt = created_date.split(' ')
		start_date = dt[0]
		tm = dt[1].split('+')
		start_time = tm[0]

		end_date = str(activities[0]['end_date'])
		dt1 = end_date.split(' ')
		tm1 = dt1[1].split('+')
		end_time = tm1[0]
		
		activity = {}
		activity['id'] = activities[0]['id']
		activity['activity_name'] = activities[0]['activity_name']
		activity['description'] = activities[0]['description']
		activity['start_date'] = start_date
		activity['start_time'] = start_time
		activity['end_time'] = end_time

		data = json.dumps({"Ack": 1, "activity": activity}, cls = DjangoJSONEncoder)
	else :
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def add_volunteersactivities(request):
	import json

	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		opportunity_id = request.POST.get('opportunity_id', None)
		activity_id = request.POST.get('activity_id', None)
		start_date = request.POST.get('start_date', None)
		end_date = request.POST.get('end_date', None)

		volunteersactivities = Volunteersactivities(
			user = User.objects.get(id = user_id),
			opportunity = Opportunities.objects.get(id = opportunity_id),
			activity = Activities.objects.get(id = activity_id),
			start_date = start_date,
			end_date = end_date
		)

		volunteersactivities.save()
		data = json.dumps({"Ack": 1, "msg": "Volunteers activity saved successfully"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def get_volunteersactivities(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder

	if request.method == 'POST':
		activity_id = request.POST.get('activity_id', None)

		cursor = connection.cursor()
		sql = "SELECT * FROM adminpanel_volunteersactivities WHERE activity_id="+activity_id
		cursor.execute(sql)
		activities = dictfetchall(cursor)

		data = json.dumps({"Ack": 1, "activities": activities}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def get_statistics(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder

	if request.method == 'POST':
		totalData = []
		opportunity_id = request.POST.get('opportunity_id', None)

		opportunityCursor = connection.cursor()
		opportunitySql = "SELECT * FROM adminpanel_opportunities WHERE id="+opportunity_id
		opportunityCursor.execute(opportunitySql)
		opportunityObjs = dictfetchall(opportunityCursor)

		for obj in opportunityObjs:
			opportunityObj = obj


		cursor = connection.cursor()
		sql = "SELECT id, activity_name FROM adminpanel_activities WHERE opportunity_id="+opportunity_id+" ORDER BY id ASC"
		cursor.execute(sql)
		activities = dictfetchall(cursor)
		activityHeader = ['Genre']

		for act in activities:
			activityHeader.append(act['activity_name'])
		totalData.append(activityHeader)

		useridsCursor = connection.cursor()
		useridsSql = "SELECT DISTINCT user_id FROM adminpanel_volunteersactivities WHERE activity_id IN (SELECT id FROM adminpanel_activities WHERE opportunity_id="+opportunity_id+")"
		useridsCursor.execute(useridsSql)
		userids = dictfetchall(useridsCursor)
		# print(userids)

		for userid in userids:
			vactivitiesCursor = connection.cursor()
			vactivitiesSql = "SELECT DISTINCT va.activity_id, CONCAT(au.first_name, ' ', au.last_name) full_name, EXTRACT(epoch FROM va.end_date - va.start_date)/3600 tothr FROM adminpanel_volunteersactivities va LEFT JOIN auth_user au ON va.user_id = au.id WHERE va.activity_id IN (SELECT id FROM adminpanel_activities WHERE opportunity_id="+opportunity_id+") AND va.user_id="+str(userid['user_id'])+" ORDER BY va.activity_id ASC"
			vactivitiesCursor.execute(vactivitiesSql)
			vactivities = dictfetchall(vactivitiesCursor)

			isFullname = False
			activityBody = []

			for item in activities:
				exist = None

				for index, vact in enumerate(vactivities):
					if isFullname == False:
						isFullname = True
						activityBody.append(vact['full_name'])

					if vact['activity_id'] == item['id']:
						exist = index

				if exist != None:
					activityBody.append(vactivities[exist]['tothr'])
				else:
					activityBody.append(0)

			totalData.append(activityBody)

		data = json.dumps({"Ack": 1, "data": totalData, "opportunity": opportunityObj}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})

	return HttpResponse(data)

def get_opportunities_by_user(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder

	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		opportunityCursor = connection.cursor()
		opportunitySql = "SELECT * FROM adminpanel_opportunities WHERE user_id_id="+user_id
		opportunityCursor.execute(opportunitySql)
		opportunityObjs = dictfetchall(opportunityCursor)
		data = json.dumps({"Ack": 1, "opportunities": opportunityObjs}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def get_organization_by_user(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		organizationCursor = connection.cursor()
		#opportunitySql = "SELECT * FROM adminpanel_organization WHERE user_id_id="+user_id
		organizationSql = "select adminpanel_organization.*,adminpanel_cordinatorrequest.* from adminpanel_organization inner join adminpanel_cordinatorrequest on adminpanel_organization.id=adminpanel_cordinatorrequest.org_id_id where adminpanel_cordinatorrequest.user_id_id="+user_id
		organizationCursor.execute(organizationSql)
		organizationObjs = dictfetchall(organizationCursor)
		data = json.dumps({"Ack": 1, "organizations": organizationObjs}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def apply_volunteer(request):
	import json

	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		opportunity_id = request.POST.get('opportunity_id', None)
		description = request.POST.get('description', None)
		
		volunteerrequirement = VolunteerRequirement(
			user_id_id = user_id,
			opportunity_id_id = opportunity_id,
			description_json = description
		)
		
		volunteerrequirement.save()
		data = json.dumps({"Ack": 1, "msg": "Volunteer Applied"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

def get_volunteersbyopportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder

	if request.method == 'POST':
		oppurtunity_id = request.POST.get('opportunity_id', None)
		cursor = connection.cursor()
		# sql = "SELECT * FROM adminpanel_cordinatorrequest WHERE oppurtunity_id="+oppurtunity_id+" and role=2"
		sql = "select auth_user.*,adminpanel_cordinatorrequest.* from adminpanel_cordinatorrequest inner join auth_user on adminpanel_cordinatorrequest.user_id_id=auth_user.id where adminpanel_cordinatorrequest.oppurtunity_id="+oppurtunity_id+" and adminpanel_cordinatorrequest.role=2"
		cursor.execute(sql)
		activities = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "voluntererArr": activities}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method allowed"})
	return HttpResponse(data)

def update_request(request):
	import json
	rtn_obj = {}
	if request.method == 'POST':
		id = request.POST.get('id',None)
		status = request.POST.get('status',None)		
		cursor1 = connection.cursor()
		cursor1.execute("update adminpanel_cordinatorrequest SET status='"+status+"' WHERE id='"+id+"'")			
		rtn_obj['msg'] = "status Updated successfully!"
		rtn_obj['Ack'] = "1"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)
	else :
		rtn_obj['msg'] = "input data by post method"
		rtn_obj['Ack'] = "0"
		data = json.dumps(rtn_obj)
		return HttpResponse(data)

# def get_opportunity_volunteer_by_user_date1(request):
# 	import json
# 	from django.core.serializers.json import DjangoJSONEncoder
# 	import datetime
# 	if request.method == 'POST':
# 		user_id = request.POST.get('user_id', None)
# 		event_date = request.POST.get('event_date', None)
# 		cursor = connection.cursor()
# 		sql = "select id, opportunity_name from adminpanel_opportunities WHERE user_id_id="+user_id+ " and date(start_date)='"+ event_date +"'"
# 		cursor.execute(sql)
# 		opportunity = dictfetchall(cursor)
# 		coordinate_data={}
# 		if opportunity:
# 			for opportunityeach in opportunity:
# 				oppurtunity_id=opportunityeach['id'];
# 				coordinate_data={}
# 				cursor2 = connection.cursor()
# 				sql2 = "select auth_user.*,adminpanel_cordinatorrequest.* from adminpanel_cordinatorrequest inner join auth_user on adminpanel_cordinatorrequest.user_id_id=auth_user.id where adminpanel_cordinatorrequest.oppurtunity_id=1 and adminpanel_cordinatorrequest.role=2"
# 				cursor2.execute(sql2)
# 				volunteers = dictfetchall(cursor2)
# 				coordinate_data['voluntererArr']=volunteers
# 			data = json.dumps({"Ack": 1, "opportunities": opportunity, "volunteer_data":coordinate_data}, cls=DjangoJSONEncoder)
# 			return HttpResponse(data)
# 		else :
# 			data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
# 			return HttpResponse(data)
# 	else :
# 		data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
# 		return HttpResponse(data)

def get_opportunity_volunteer_by_user_date(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	import datetime
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		event_date = request.POST.get('event_date', None)
		cursor = connection.cursor()
		# sql = "select * from adminpanel_opportunities WHERE user_id_id="+str(user_id)+ " and date(start_date)='"+ event_date +"'"
		sql = "select adminpanel_opportunities.*,adminpanel_cordinatorrequest.status from adminpanel_opportunities inner join adminpanel_cordinatorrequest on (adminpanel_cordinatorrequest.oppurtunity_id=adminpanel_opportunities.id and adminpanel_cordinatorrequest.user_id_id != adminpanel_opportunities.user_id_id) WHERE adminpanel_cordinatorrequest.user_id_id="+str(user_id)+" and adminpanel_opportunities.user_id_id !="+str(user_id)+ " and date(adminpanel_opportunities.start_date)='"+ event_date +"'"
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		if (len(opportunity)==0):
			sql3 = "select * from adminpanel_opportunities WHERE user_id_id="+str(user_id)+ " and date(start_date)='"+ event_date +"'"
			cursor3 = connection.cursor()
			cursor3.execute(sql3)
			opportunity= dictfetchall(cursor3)	
		v_data={}
		coordinate_data={}
		if opportunity:
			for i in range(len(opportunity)):
				o_id=opportunity[i]['id']
				opportunity[i]['opportunity_id']=opportunity[i]['id']
				cursor2 = connection.cursor()
				sql2 = "select auth_user.*,adminpanel_cordinatorrequest.* from adminpanel_cordinatorrequest inner join auth_user on adminpanel_cordinatorrequest.user_id_id=auth_user.id where adminpanel_cordinatorrequest.oppurtunity_id="+str(o_id)+" and adminpanel_cordinatorrequest.role=2"
				cursor2.execute(sql2)
				volunteers = dictfetchall(cursor2)
				opportunity[i]['volunteers']=volunteers
				oppurtunityArr=opportunity[i]
				coordinate_data[i]=oppurtunityArr	

			data = json.dumps({"Ack": 1, "event_data":coordinate_data}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
		else :
			data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
	else :
		data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
		return HttpResponse(data)

# def logout_page(request):
# 	import json
# 	rtn_obj = {}
# 	logout(request)
# 	rtn_obj['ack'] = "1"
# 	rtn_obj['msg_error'] = "Logout Successfully"
# 	data = json.dumps(rtn_obj)
# 	return HttpResponse(data)

def save_opportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		opportunity_id = request.POST.get('opportunity_id', None)
		user_id = request.POST.get('user_id', None)
		save_opportunity = OpportunitySaved(
			opportunity_id = opportunity_id,
			user_id = user_id
		)
		save_opportunity.save()
		data = json.dumps({"Ack": 1, "msg": "Opportunity successfully saved"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Please try again"})
	return HttpResponse(data)

def opportunity_apply(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		org_id = request.POST.get('org_id', None)
		opportunity_id = request.POST.get('opportunity_id', None)
		user_id = request.POST.get('user_id', None)
		url = request.POST.get('url', None)
		answers = request.POST.get('answer')
		answers = json.loads(answers)

		cordinatorRequest = CordinatorRequest(
			user_id = User.objects.get(id=str(user_id)),
			org_id = Organization.objects.get(id=str(org_id)),
			status = 'Pending',
			role = int(2),
			oppurtunity_id = int(opportunity_id),
			is_url = False if url == 'false' else True
		)
		cordinatorRequest.save()

		# opportunitiesapplied = Opportunitiesapplied(
		# 	opportunity = Opportunities.objects.get(id=opportunity_id),
		# 	user = User.objects.get(id=user_id),
		# 	is_url = url
		# )

		if answers:
			for answer in answers:
				opportunityanswers = Opportunityanswers(
					opportunity = Opportunities.objects.get(id=opportunity_id),
					user = User.objects.get(id=user_id),
					question = OpportunityQuestions.objects.get(id=answer['q_id']),
					answer = answer['answer']
				)
				opportunityanswers.save()
		data = json.dumps({"Ack": 1, "msg": "Successfully applied for this opportunity"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Only post method applied"})
	return HttpResponse(data)
		
# def get_saved_opportunity(request):
# 	import json
# 	from django.core.serializers.json import DjangoJSONEncoder
# 	if request.method == 'POST':
# 		user_id = request.POST.get('user_id', None)
# 		cursor = connection.cursor()
# 		sql = "select * from adminpanel_opportunitysaved WHERE user_id="+str(user_id)
# 		cursor.execute(sql)
# 		opportunity = dictfetchall(cursor)
# 		opportunity_data={}
# 		if opportunity:
# 			for i in range(len(opportunity)):
# 				o_id=opportunity[i]['id']
# 				cursor2 = connection.cursor()
# 				sql2 = "select * from adminpanel_opportunities WHERE id="+str(o_id)
# 				cursor2.execute(sql2)
# 				opportunities = dictfetchall(cursor2)
# 				opportunity[i]['opportunities']=opportunities
# 			data = json.dumps({"Ack": 1, "event_data":opportunity}, cls=DjangoJSONEncoder)
# 			return HttpResponse(data)
# 		else :
# 			data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
# 			return HttpResponse(data)
# 	else :
# 		data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
# 		return HttpResponse(data)

def get_saved_opportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	import datetime
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		event_date = request.POST.get('event_date', None)
		cursor = connection.cursor()
		#sql = "select * from adminpanel_opportunities WHERE user_id_id="+str(user_id)+ " and date(start_date)='"+ event_date +"'"
		sql = "select adminpanel_opportunities.* from adminpanel_opportunities inner join adminpanel_opportunitysaved on adminpanel_opportunities.id=adminpanel_opportunitysaved.opportunity_id WHERE adminpanel_opportunitysaved.user_id="+str(user_id)+"  and date(adminpanel_opportunities.start_date)='"+ event_date +"'"
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		v_data={}
		coordinate_data={}
		if opportunity:
			for i in range(len(opportunity)):
				o_id=opportunity[i]['id']
				opportunity[i]['opportunity_id']=opportunity[i]['id']
				cursor2 = connection.cursor()
				sql2 = "select auth_user.*,adminpanel_cordinatorrequest.* from adminpanel_cordinatorrequest inner join auth_user on adminpanel_cordinatorrequest.user_id_id=auth_user.id where adminpanel_cordinatorrequest.oppurtunity_id="+str(o_id)+" and adminpanel_cordinatorrequest.role=2"
				cursor2.execute(sql2)
				volunteers = dictfetchall(cursor2)
				opportunity[i]['volunteers']=volunteers
				oppurtunityArr=opportunity[i]
				coordinate_data[i]=oppurtunityArr
				v_data=coordinate_data
			data = json.dumps({"Ack": 1, "event_data":v_data}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
		else :
			data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
	else :
		data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
		return HttpResponse(data)

def remove_save_opportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		id = request.POST.get('id', None)
		cursor = connection.cursor()
		sql = "delete from adminpanel_opportunitysaved WHERE id="+str(id)
		cursor.execute(sql)
		data = json.dumps({"Ack": 1, "msg": "Opportunity successfully removed"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Please try again"})
	return HttpResponse(data)

def get_opportunities_savedstatus(request):
	import json
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		cursor = connection.cursor()
		sql = """select AO.id, AO.opportunity_name, AO.description,AO.user_id_id, AO.image, AU.first_name, AU.last_name, AO.org_id_id 
					from adminpanel_opportunities AO
					left join auth_user AU
					on AO.user_id_id = AU.id 
					order by AO.id desc"""
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		if opportunity:
				for i in range(len(opportunity)):
					o_id=opportunity[i]['id']
					cursor2 = connection.cursor()
					sql2 = "select count(*) as save_count from adminpanel_opportunitysaved WHERE opportunity_id="+str(o_id)+" and user_id="+str(user_id)
					cursor2.execute(sql2)
					savedopportunities = dictfetchall(cursor2)
					opportunity[i]['is_saved']=savedopportunities

					question_cursor = connection.cursor()
					question_sql = "select * from adminpanel_opportunityquestions where opportunity_id ="+str(o_id)
					question_cursor.execute(question_sql)
					questions = dictfetchall(question_cursor)
					opportunity[i]['questions'] = questions

					shared_conn = connection.cursor()
					shared_sql = "select count(*) from adminpanel_opportunityshared where opportunity_id = " + str(o_id)
					shared_conn.execute(shared_sql)
					shared_res = dictfetchall(shared_conn)
					# print(shared_res)
					if shared_res[0]['count'] > 0:
						opportunity[i]['shared'] = 1
					else:
						opportunity[i]['shared'] = 0

					if opportunity[i]['user_id_id'] == str(user_id):
						opportunity[i]['is_apply'] = 0
					else:
						opportunity[i]['is_apply'] = 1
						apply_cursor = connection.cursor()
						apply_sql = "select * from adminpanel_cordinatorrequest where oppurtunity_id ="+str(o_id)+" and user_id_id = "+str(user_id)
						apply_cursor.execute(apply_sql)
						applystatus = dictfetchall(apply_cursor)
						if applystatus:
							opportunity[i]['is_apply'] = 2
							opportunity[i]['application_status'] = applystatus[0]['status']

	data = json.dumps({"Ack": 1, "opportunities": opportunity, "image_url": settings.BASE_URL + "/media/"})
	return HttpResponse(data)

def get_myapplied_opportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		cursor = connection.cursor()
		sql = "select * from adminpanel_cordinatorrequest WHERE user_id_id="+str(user_id)
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		if opportunity:
			for i in range(len(opportunity)):
				o_id=opportunity[i]['oppurtunity_id']
				cursor2 = connection.cursor()
				sql2 = "select * from adminpanel_opportunities WHERE id="+str(o_id)
				cursor2.execute(sql2)
				opportunities = dictfetchall(cursor2)
				opportunity[i]['opportunities']=opportunities
			data = json.dumps({"Ack": 1, "event_data":opportunity}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
		else :
			data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
	else :
		data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
		return HttpResponse(data)

def share_opportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		opportunity_id = request.POST.get('opportunity_id', None)
		user_id = request.POST.get('user_id', None)
		facebook = request.POST.get('facebook', None)
		twitter = request.POST.get('twitter', None)
		linkedin = request.POST.get('linkedin', None)
		google = request.POST.get('google', None)
		save_opportunity = OpportunityShared(
			opportunity_id = opportunity_id,
			user_id = user_id,
			facebook = facebook,
			twitter = twitter,
			linkedin = linkedin,
			google = google
		)
		save_opportunity.save()
		data = json.dumps({"Ack": 1, "msg": "Opportunity successfully shared"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Please try again"})
	return HttpResponse(data)

def share_opportunity_update(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		opportunity_id = request.POST.get('opportunity_id', None)
		user_id = request.POST.get('user_id', None)
		facebook = request.POST.get('facebook', None)
		twitter = request.POST.get('twitter', None)
		linkedin = request.POST.get('linkedin', None)
		google = request.POST.get('google', None)
		id = request.POST.get('id', None)
		cursor1 = connection.cursor()
		cursor1.execute("update adminpanel_opportunityshared SET facebook='"+facebook+"', twitter='"+twitter+"', linkedin='"+linkedin+"', google='"+google+"' WHERE id='"+id+"'")
		data = json.dumps({"Ack": 1, "msg": "Opportunity successfully shared"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Please try again"})
	return HttpResponse(data)

def get_shared_opportunity(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	import datetime
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		event_date = request.POST.get('event_date', None)
		cursor = connection.cursor()
		#sql = "select * from adminpanel_opportunities WHERE user_id_id="+str(user_id)+ " and date(start_date)='"+ event_date +"'"
		sql = "select adminpanel_opportunities.* from adminpanel_opportunities inner join adminpanel_opportunityshared on adminpanel_opportunities.id=adminpanel_opportunityshared.opportunity_id WHERE adminpanel_opportunityshared.user_id="+str(user_id)+"  and date(adminpanel_opportunities.start_date)='"+ event_date +"'"
		cursor.execute(sql)
		opportunity = dictfetchall(cursor)
		v_data={}
		coordinate_data={}
		if opportunity:
			for i in range(len(opportunity)):
				o_id=opportunity[i]['id']
				opportunity[i]['opportunity_id']=opportunity[i]['id']
				cursor2 = connection.cursor()
				sql2 = "select auth_user.*,adminpanel_cordinatorrequest.* from adminpanel_cordinatorrequest inner join auth_user on adminpanel_cordinatorrequest.user_id_id=auth_user.id where adminpanel_cordinatorrequest.oppurtunity_id="+str(o_id)+" and adminpanel_cordinatorrequest.role=2"
				cursor2.execute(sql2)
				volunteers = dictfetchall(cursor2)
				opportunity[i]['volunteers']=volunteers
				oppurtunityArr=opportunity[i]
				coordinate_data[i]=oppurtunityArr
				v_data=coordinate_data
			data = json.dumps({"Ack": 1, "event_data":v_data}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
		else :
			data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
			return HttpResponse(data)
	else :
		data = json.dumps({"Ack": 0}, cls=DjangoJSONEncoder)
		return HttpResponse(data)


def update_opportunity(request):
	import json

	if request.method == 'POST':
		id = request.POST.get('id', None)
		opportunity_name = request.POST.get('opportunity_name', None)
		description = request.POST.get('description', None)
		no_of_volunteers = request.POST.get('no_of_volunteers', None)
		address = request.POST.get('address', None)

		# category_ids = request.POST.get('category_id')
		# category_ids = json.loads(category_ids)

		# reminders = request.POST.get('reminders')
		# reminders = json.loads(reminders)

		parent_id = request.POST.get('parent_id', None)
		no_ofyear = request.POST.get('no_ofyear', None)
		start_date = request.POST.get('start_date', None)
		end_date = request.POST.get('end_date', None)
		questions = request.POST.get('questions')
		questions = json.loads(questions)

		# print(questions)
		# return HttpResponse(1)
		
		if len(request.FILES) != 0:
			image_file = request.FILES['file']
		else :
			image_file = ''

		# volunteer_id = request.POST.get('volunteer_id', None)
		# is_valid = request.POST.get('is_valid', None)
		# is_public = request.POST.get('is_public', None)
		# is_recurring = request.POST.get('is_recurring', None)
		# parent_opportunity = request.POST.get('parent_opportunity', None)


		# cursor = connection.cursor()
		# sql = "select * from adminpanel_cordinatorrequest where user_id_id='"+ user_id +"'"
		# cursor.execute(sql)
		# getorgId = dictfetchall(cursor)

		# org_id_id = getorgId[0]['org_id_id']

		# user = User.objects.get(id=user_id)
		# organization = Organization.objects.get(id = org_id_id)
		# category = ActivityCategory.objects.get(id = category_id)
		# volunteer = Volunteer.objects.get(id = volunteer_id)

		opportunitiy = Opportunities.objects.get(id = id)
		opportunitiy.opportunity_name = opportunity_name
		opportunitiy.description = description
		opportunitiy.no_of_volunteers = no_of_volunteers
		opportunitiy.address = address
		opportunitiy.parent_id = parent_id
		opportunitiy.no_ofyear = no_ofyear
		opportunitiy.start_date = start_date
		opportunitiy.end_date = end_date
		opportunitiy.save()
		
		# if image_file:
		# 	imgthumb = Image.open(settings.MEDIA_ROOT+"/"+opportunitiy.image.name)
		# 	imgthumb.save(settings.MEDIA_ROOT + '/' + opportunitiy.image.name)
		# 	opportunitiy.image = opportunitiy.image.name
		# 	opportunitiy.save()

		# opportunityObj = Opportunities.objects.latest('id')

		# for cat in category_ids:
		# 	catObj = ActivityCategory.objects.get(id = cat['id'])
		# 	opportunityCategories = OpportunityCategories(
		# 		opportunity_id = opportunityObj,
		# 		category_id = catObj
		# 	)
		# 	opportunityCategories.save()

		# for reminder in reminders:
		# 	rem = Reminders(
		# 		start_date = reminder['date'],
		# 		before_hour = reminder['hour'],
		# 		opportunity_id = opportunityObj
		# 	)
		# 	rem.save()

		# for question in questions:
		# 	question = OpportunityQuestions(
		# 		opportunity = opportunityObj,
		# 		question = question['question']
		# 	)
		# 	question.save()

		data = json.dumps({"Ack": 1, "msg": "Opportunity successfully saved"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})

	return HttpResponse(data)

def addvolunteerbyowner(request):
	import json
	if request.method == 'POST':
		o_id=request.POST.get('opportunity_id', None)
		email= request.POST.get('email', None)
		first_name= request.POST.get('first_name', None)
		last_name= request.POST.get('last_name', None)
		password= '123456'
		cursor = connection.cursor()
		sql="select id from auth_user where email = '"+ str(email) +"'"
		cursor.execute(sql)
		userdata = dictfetchall(cursor)
		if userdata:
			user_id=userdata[0]['id']
		else:
			import base64
			import time
			user = User.objects.create_user(
			password=password,
			is_superuser=False,
			username=email,
			first_name=first_name,
			last_name=last_name,
			email=email,
			is_staff=False,
			is_active=True
			)
			user.save()
			user_id=user.id

		apply_coordinator = CordinatorRequest(
			user_id_id=user_id,
			org_id_id=2,
			status="Approved",
			address='N/A',
			employee_number=0,
			oppurtunity_id=o_id,
			role=2
			)
		apply_coordinator.save()
		msg_html='Hello '+first_name+' </br> You have added as a volunteer to the opportunity.To see the opportunity detail click on the link.</br><a href="http://111.93.169.90/team4/inteerApp/#/feed-details/'+o_id+'"></a>'
		# send_mail('Added as a volunteer', 'InterApp', 'tanay@natitsolved.com', [email], html_message=msg_html)
		data = json.dumps({"Ack": 1, "msg": "Volunteer Added for opportunitiy"})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)




# def get_volunteers_suggestion(request):
# 	import json

# 	if request.method == 'POST':
# 		name = request.POST.get('name', None)
# 		cursor = connection.cursor()
# 		sql = "select id,volunteer_name from adminpanel_volunteer where lower(volunteer_name) like lower('%"+name+"%')"
# 		#  sql = "select id,first_name,last_name from auth_user where lower(first_name) like lower('%"+name+"%') or lower(last_name) like lower('%"+name+"%')"
# 		//print(sql)
# 		cursor.execute(sql)
# 		volunteers = dictfetchall(cursor)
# 		data = json.dumps({"Ack": 1, "volunteers": volunteers})
# 	else:
# 		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
# 	return HttpResponse(data)	

# def get_volunteers_suggestion(request):
# 	import json

# 	if request.method == 'POST':
# 		name = request.POST.get('name', None)
# 		cursor = connection.cursor()
# 		sql = "select * from adminpanel_volunteer where lower(volunteer_name) like lower('%"+name+"%')"
		
# 		cursor.execute(sql)
# 		volunteers = dictfetchall(cursor)
# 		data = json.dumps({"Ack": 1, "volunteers": volunteers})
# 	else:
# 		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
# 	return HttpResponse(data)


def get_volunteers_suggestion(request):
	import json

	if request.method == 'POST':
		# name = request.POST.get('name', None)
		cursor = connection.cursor()
		#sql = "select * from adminpanel_volunteer"
		sql = "SELECT DISTINCT(RTRIM(CONCAT(LTRIM(RTRIM(first_name)) , ' ' , LTRIM(RTRIM(last_name))))) AS Full_Name,user_id_id FROM auth_user INNER JOIN adminpanel_cordinatorrequest ON auth_user.id = adminpanel_cordinatorrequest.user_id_id AND role=2"
		
		cursor.execute(sql)
		volunteers = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "volunteers": volunteers})
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

def getengage_by_userdate(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		user_id = request.POST.get('user_id', None)
		start_date = request.POST.get('start_date', None)
		end_date = request.POST.get('end_date', None)
		# sql = "SELECT * FROM adminpanel_cordinatorrequest cr LEFT JOIN adminpanel_opportunities o ON cr.oppurtunity_id = o.id WHERE cr.user_id_id = "+user_id+" AND o.start_date = '"+start_date+"' AND o.end_date = '"+end_date+"'"
		sql = "SELECT *,EXTRACT(EPOCH FROM (o.end_date - o.start_date)/3600) as time_cal FROM adminpanel_cordinatorrequest cr LEFT JOIN adminpanel_opportunities o ON cr.oppurtunity_id = o.id WHERE cr.user_id_id = "+user_id+" AND o.start_date >= '"+start_date+"' AND o.end_date <= '"+end_date+"'"
		print(sql)
		cursor = connection.cursor()
		cursor.execute(sql)
		opportunities = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "opportunities": opportunities}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)

# def getengage_by_userdate(request):
# 	import json
# 	import datetime
# 	if request.method == 'POST':
# 		user_id = request.POST.get('user_id', None)
# 		start_date1 = request.POST.get('start_date', None)
# 		end_date1 = request.POST.get('end_date', None)
# 		cursor = connection.cursor()
# 		#sql = "select id from adminpanel_opportunities WHERE user_id_id='"+user_id+"' and (start_date >='"+start_date1+"' and end_date <='"+end_date1+"')"
# 		sql ="SELECT id, opportunity_name FROM adminpanel_opportunities WHERE date(start_date) >= '"+start_date+"' AND date(end_date) < ('"+end_date+"')"

		
# 		#sql = "select id,opportunity_name,start_date from adminpanel_opportunities"
		
# 		cursor.execute(sql)
# 		opportunity = dictfetchall(cursor)
# 		data = json.dumps({"Ack": 1, "opportunities": opportunity})
# 	return HttpResponse(data)


def getengage_by_date(request):
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	if request.method == 'POST':
		
		start_date = request.POST.get('start_date', None)
		end_date = request.POST.get('end_date', None)
		# sql = "SELECT * FROM adminpanel_cordinatorrequest cr LEFT JOIN adminpanel_opportunities o ON cr.oppurtunity_id = o.id WHERE cr.user_id_id = "+user_id+" AND o.start_date = '"+start_date+"' AND o.end_date = '"+end_date+"'"
		sql = "SELECT *,EXTRACT(EPOCH FROM (o.end_date - o.start_date)/3600) as time_cal FROM adminpanel_cordinatorrequest cr LEFT JOIN adminpanel_opportunities o ON cr.oppurtunity_id = o.id WHERE o.start_date >= '"+start_date+"' AND o.end_date <= '"+end_date+"'"
		# print(sql)
		cursor = connection.cursor()
		cursor.execute(sql)
		opportunities = dictfetchall(cursor)
		#print(opportunities)

		

		# for opportunity in opportunities:
		# 	opportunity_data={}
		# 	opportunity_data['name']=opportunity['opportunity_name']
		# 	return HttpResponse(opportunity_data)

		data = json.dumps({"Ack": 1, "opportunities": opportunities}, cls=DjangoJSONEncoder)
	else:
		data = json.dumps({"Ack": 0, "msg": "Post method supported only"})
	return HttpResponse(data)



def get_subscription(self):
	import json

	cursor13 = connection.cursor()
	sql3 = "select * from adminpanel_subscription"
	cursor13.execute(sql3)
	subscription = dictfetchall(cursor13)

	data = json.dumps({"Ack": 1, "subscription": subscription})

	return HttpResponse(data)

def get_organization_by_id(request):
	import json
	import datetime
	if request.method == 'POST':
		id = request.POST.get('id', None)
		cursor = connection.cursor()
		sql = "select * FROM adminpanel_organization WHERE id="+id+""
		cursor.execute(sql)
		organization = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "organization": organization})
	return HttpResponse(data)



def get_user_volunteer(request):
	import json
	import datetime
	if request.method == 'POST':
		# id = request.POST.get('id', None)
		cursor = connection.cursor()
		# sql = "select id FROM adminpanel_userprofile where role_id ='2'"
		#  adu LEFT JOIN auth_user au ON adu.user_id_id = au.id WHERE adu.role_id='2'
		sql = "SELECT adu.id,au.first_name,au.last_name FROM adminpanel_userprofile adu LEFT JOIN auth_user au ON adu.user_id_id = au.id WHERE adu.role_id='2'"
		cursor.execute(sql)
		vuser = dictfetchall(cursor)
		data = json.dumps({"Ack": 1, "volunteeruser": vuser})
	return HttpResponse(data)

def sample(request):
	import csv
	import psycopg2
	conn = psycopg2.connect("host=138.68.12.41 dbname=db_inter user=social_django_user password=Host@123456")
	cur = conn.cursor()
	with open('/var/www/html/inteer/djangogirls/webservice/Master_Sheet_All_new.csv', 'r') as f:
		reader = csv.reader(f)
		next(reader)  # Skip the header row.
		for row in reader:
			cur.execute("insert into adminpanel_organization (organization_name, parent_id, address, tax_id, email, web_url, phone, cause, about_us, our_activity, why_us, photo, address1, event1, event2, event3, fb_url, irs_rank, phone2, submission_date) values ('"+row[0]+"','"+row[1]+"','"+row[2]+"','"+row[3]+"','"+row[4]+"','"+row[5]+"','"+row[6]+"','"+row[7]+"','"+row[8]+"','"+row[9]+"','"+row[10]+"','"+row[11]+"','"+row[12]+"','"+row[13]+"','"+row[14]+"','"+row[15]+"','"+row[16]+"','"+row[17]+"','"+row[18]+"','"+row[19]+"')")
	conn.commit()

def get_oppoptunity_volunteertime(request):
	userarr=[]
	import json
	from django.core.serializers.json import DjangoJSONEncoder
	cursor = connection.cursor()
	start_date = request.POST.get('start_date', None)
	end_date = request.POST.get('end_date', None)
	# sql = "select id FROM adminpanel_userprofile where role_id ='2'"
	#  adu LEFT JOIN auth_user au ON adu.user_id_id = au.id WHERE adu.role_id='2'
	sql = "select adminpanel_opportunities.*, adminpanel_cordinatorrequest.* from adminpanel_opportunities INNER JOIN adminpanel_cordinatorrequest on adminpanel_opportunities.id=adminpanel_cordinatorrequest.oppurtunity_id where adminpanel_cordinatorrequest.role='2'"
	cursor.execute(sql)
	alluserDetails = dictfetchall(cursor)
	'''for userDetails in alluserDetails:
		usrdt={}
		usrdt['user_id']=int(alluserDetails['user_id_id'])
		usrdt['opportunity_name']=str(alluserDetails['opportunity_name'])
		usrdt['start_date']=str(alluserDetails['start_date'])
		usrdt['end_date']=str(alluserDetails['end_date'])
		userarr.append(usrdt)'''
	data = json.dumps({"Ack": 1, "volunteeruser": len(alluserDetails)}, cls=DjangoJSONEncoder)
	return HttpResponse(data)