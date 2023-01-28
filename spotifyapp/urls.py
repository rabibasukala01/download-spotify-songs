
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='login_page'),
    path('gg', views.callback, name='callback'),
    path('download', views.ytdown, name='ytdown'),



]
