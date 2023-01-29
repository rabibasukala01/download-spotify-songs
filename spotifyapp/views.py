from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import requests
import base64
from .utlis import client_auth_url, download_audio, name_to_yt_video_id_generator, update_or_create_tokens, is_user_authenticated
from .models import SpotifyToken
from spotify.settings import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
# send prepare url to frontend so that client can click


# main home page
def blank(request):
    redirect('home')


def home(request):

    if not is_user_authenticated(request.session.session_key):
        context = {"authenticated": False,
                   'a': [1, 3]
                   }
        return render(request, 'home.html', context)

    # extracting user info
    obj = SpotifyToken.objects.get(user=request.session.session_key)
    profile_url = 'https://api.spotify.com/v1/me'
    headers = {
        'Authorization': f'Bearer {obj.access_token}',
        'Content-Type': 'application/json',
    }

    user_info = requests.get(profile_url, headers=headers).json()
    # print(r.json())
    display_name = user_info.get('display_name')
    user_spotify_id = user_info.get('id')
    user_spotify_pfp = user_info.get('images')[0]['url']
    # print(user_spotify_pfp)
    # print(display_name)

    # extraction user playlists
    parameters = {

        'offset': 20,

    }

    playlist_imgs = []

    playlist_url = f'https://api.spotify.com/v1/users/sx6tg6nghw29oisjtij33iky6/playlists'
    playlist_response = requests.get(
        playlist_url, headers=headers).json().get('items')

    playlists_info = []

    for playlist in playlist_response:

        dic = {'name': playlist.get('name'),
               'id': playlist.get('id')
               }
        playlists_info.append(dic)

        # if playlist_imgs != None and len(playlist_imgs) > 1:
        #     playlist_imgs.append(playlist.get('images')[0])

    # print(playlist_info)
    # get saved songs
    # parameter = {
    #     'offset': 20

    # }
    # saved_info = requests.get(
    #     'https://api.spotify.com/v1/me/tracks', headers=headers, params=parameter).json()
    # print(saved_info)

    context = {"authenticated": True,
               'display_name': display_name,
               'user_spotify_id': user_spotify_id,
               'user_spotify_pfp': user_spotify_pfp,
               'playlists_info': playlists_info
               #    'playlist_imgs': playlist_imgs

               }
    return render(request, 'home.html', context)


def log_in(request):

    context = {
        "client_auth_url": client_auth_url(),
    }

    return render(request, 'login_page.html', context)


# callback after login and generating  token  ig
def callback(request):

    CODE = request.GET.get('code')  # from spotify
    state = request.GET.get('state')  # from spotify

    data = {
        'grant_type': "authorization_code",
        'code': CODE,
        'redirect_uri': REDIRECT_URI,
    }
    # enncoded client creds with b64
    # str to byte follow by b64encoded[note for b64 we need to str>>b]
    # decode bytestr but not b64encode-so that final result in only b64
    encoded_creds = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    header = {
        # <base64 encoded client_id:client_secret>
        'Authorization': f"Basic {encoded_creds}",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    # post to spotify to generate token , expire time etc
    result = requests.post(
        'https://accounts.spotify.com/api/token', data=data, headers=header).json()

    access_token = result.get('access_token')
    refresh_token = result.get('refresh_token')
    expires_in = result.get('expires_in')
    token_type = result.get('token_type')

    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create_tokens(request.session.session_key, access_token,
                            refresh_token, token_type, expires_in)

    return redirect('home')

    # return render(request, 'spotify.html')


def playlists(request, playlist_id):

    return HttpResponse(f"{playlist_id} asdad")


def ytdown(request):
    # video_id = 'b73BI9eUkjM'
    audio_file = download_audio()
    # print(audio_file[0])
    # ------------------------------------------
    response = HttpResponse(requests.get(
        audio_file[0]).content, content_type='audio/mp3')
    response['Content-Disposition'] = f'attachment; filename={audio_file[1]}.mp3'
    return response

    # TODO
    # what if wee use fileResponse , io for performance but idk how to
    # ------------------------------------------
