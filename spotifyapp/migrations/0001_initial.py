# Generated by Django 3.2.16 on 2023-01-26 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100, unique=True)),
                ('access_token', models.CharField(max_length=150)),
                ('refresh_token', models.CharField(max_length=150)),
                ('token_type', models.CharField(max_length=40)),
                ('expires_in', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]