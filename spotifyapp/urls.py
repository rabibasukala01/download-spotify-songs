
from django.urls import path
from . import views
urlpatterns = [
    path('', views.blank, name='blank'),
    path('home', views.home, name='home'),
    path('gg', views.callback, name='callback'),
    path('login', views.log_in, name='log_in'),
    path('playlists/<str:playlist_id>/', views.playlists, name='playlists'),
    path('download', views.ytdown, name='ytdown'),


]
