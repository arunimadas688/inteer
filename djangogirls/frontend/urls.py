from django.conf.urls import  include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	url(r'^$', views.home_index, name='home_index'),
	url(r'^home/', views.home_index, name='home_index'),
	url(r'^login/', views.login_user, name='login_user'),
	url(r'^login-submit/', views.login_user_submit, name='login_user_submit'),
	url(r'^forgotpassword/', views.forgot_password, name='forgot_password'),
	url(r'^forgotpasswordsubmit/', views.forgot_password_submit, name='forgot_password_submit'),
	url(r'^resetpassword/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',views.reset_password,name='reset_password'),
	url(r'^reset-password-submit/', views.reset_password_submit, name='reset_password_submit'),
	url(r'^logout/', views.logout_page, name='logout_page'),
	url(r'^signup/', views.typeof_signup, name='typeof_signup'),
	url(r'^register-user/', views.register_user, name='register_user'),
	url(r'^activation/(?P<base64string>\d+)/', views.activate_link, name='activate_link'),
	url(r'^dashboard/', views.user_profile, name='user_profile'),
	url(r'^editprofile/', views.profile_edit, name='profile_edit'),
	url(r'^becomecoordinator/', views.becomecoordinator, name='becomecoordinator'),
	url(r'^become-coordinator/', views.become_coordinator, name='become_coordinator'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns +=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
