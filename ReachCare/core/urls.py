from django.urls import path

from . import views

urlpatterns = [
    path('sms', views.sms_response, name='sms'),
    path('', views.home_view, name="home"),
    path('login', views.login_view, name='login'),
    path('account', views.account_view, name="account")

]
