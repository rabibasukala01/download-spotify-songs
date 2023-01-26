from django.db import models

# Create your models here.


class SpotifyToken(models.Model):
    user = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(max_length=150)
    refresh_token = models.CharField(max_length=150)
    token_type = models.CharField(max_length=40)
    expires_in = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
