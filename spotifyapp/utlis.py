import base64
from requests import post
import youtube_dl
from googleapiclient.discovery import build
from spotify.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, yt_API_KEY
from random import randint
from requests import Request
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta

# https://github.com/googleapis/google-api-python-client/blob/main/docs/README.md
# for other services in case
# https://github.com/googleapis/google-api-python-client/blob/main/docs/dyn/index.md


def client_auth_url():
    url = 'https://accounts.spotify.com/authorize'
    params = {
        "response_type": 'code',
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "state": randint(1, 20),
        "show_dialog": False

    }
    return Request('GET', url, params=params).prepare().url


def update_or_create_tokens(session_id, access_token, refresh_token, token_type, expires_in):
    # converting in actual time format
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    # checking if already there is token or not
    user_token = SpotifyToken.objects.filter(user=session_id)
    if user_token.exists():
        tokens = user_token[0]
    else:
        tokens = None
    # if exist ,just update
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.token_type = token_type
        tokens.expires_in = expires_in
        tokens.save(update_fields=['access_token',
                    'refresh_token', 'expires_in', 'token_type'])
    # if not save new tokken
    else:
        tokens = SpotifyToken(user=session_id, access_token=access_token,
                              refresh_token=refresh_token, expires_in=expires_in, token_type=token_type)
        tokens.save()


def refresh_the_token(tokens, session_id):
    refresh_token = tokens.refresh_token
    encoded_creds = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f"Basic {encoded_creds}",
        'Content-Type': "application/x-www-form-urlencoded"

    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,

    }

    response = post("https://accounts.spotify.com/api/token",
                    data=data, headers=headers).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')
    # then update
    update_or_create_tokens(session_id, access_token,
                            refresh_token, token_type, expires_in)


def is_user_authenticated(session_id):
    user_token = SpotifyToken.objects.filter(user=session_id)
    if user_token.exists():
        tokens = user_token[0]
    else:
        tokens = None
    if tokens:
        expiry_time = tokens.expires_in
        if expiry_time <= timezone.now():
            refresh_the_token(tokens, session_id)
        return True

    return False


def name_to_yt_video_id_generator(searchQuery):
    youtube_service = build('youtube', 'v3', developerKey=yt_API_KEY)
    result = youtube_service.search().list(
        part='snippet',
        q=f'{searchQuery}',
        safeSearch='moderate',
        type='video',
        videoDuration='medium',
        maxResults=1,

    )

    videoID = result.execute()['items'][0]['id']['videoId']
    return videoID


def download_audio(video_id='b73BI9eUkjM'):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', None)
        audio_url = info.get('url', None)

        return audio_url, title


if __name__ == '__main__':
    # for testing only
    # video_id = name_to_yt_video_id_generator(
    #     'Adele - Easy On Me ')

    print(download_audio()[0])
