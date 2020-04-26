from django.urls import path

from . import views

urlpatterns = [
    path('sms', views.sms_response, name='sms'),
    # path('login/',
    #      login_view,
    #      name='login'),
    # path('logout/',
    #      logout_view,
    #      name='logout'),
    # path('/', home_view, name="home")
]
