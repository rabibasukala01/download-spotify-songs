
from django.urls import path
from . import views
urlpatterns = [
    path('login', views.log_in, name='log_in'),
    path('home', views.home, name='home'),
    path('gg', views.callback, name='callback'),
    path('download', views.ytdown, name='ytdown'),



]
