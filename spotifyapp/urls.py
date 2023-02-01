
from django.urls import path
from . import views
urlpatterns = [
    path('', views.blank, name='blank'),
    path('login', views.log_in, name='log_in'),
    path('home', views.home, name='home'),
    path('gg', views.callback, name='callback'),
    path('playlists/<str:playlist_id>/', views.playlists, name='playlists'),
    path('download/<str:name><str:artist>', views.download, name='download'),
    path('log_out', views.log_out, name='log_out'),


]
