
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('gg', views.callback, name='callback'),
    path('download', views.ytdown, name='ytdown'),



]
