from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import requests
import base64
from .utlis import client_auth_url, download_audio, name_to_yt_video_id_generator, update_or_create_tokens, is_user_authenticated
from .models import SpotifyToken
from spotify.settings import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET


# main home page
def blank(request):
    redirect('log_in')


def home(request):

    if not is_user_authenticated(request.session.session_key):
        context = {"authenticated": False,

                   }
        return render(request, 'home.html', context)

    # extracting user info
    profile_url = 'https://api.spotify.com/v1/me'
    obj = SpotifyToken.objects.get(user=request.session.session_key)
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
        'limit': 1,

    }

    playlist_imgs = []

    # playlist_url = f'https://api.spotify.com/v1/users/sx6tg6nghw29oisjtij33iky6/playlists'
    playlist_url = 'https://api.spotify.com/v1/me/playlists'
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

    context = {"authenticated": True,
               'display_name': display_name,
               'user_spotify_id': user_spotify_id,
               'user_spotify_pfp': user_spotify_pfp,
               'playlists_info': playlists_info,
               #    'playlist_imgs': playlist_imgs
               'likedsongs': 'likedsongs',

               }
    return render(request, 'home.html', context)


def log_in(request):

    # send prepare url to frontend so that client can click
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


def ms_to_min(ms):
    sec = ms/1000
    return round(int(sec)/60, 2)


def playlists(request, playlist_id):
    print(playlist_id)
    songs_info = []
    obj = SpotifyToken.objects.get(user=request.session.session_key)
    headers = {
        'Authorization': f'Bearer {obj.access_token}',
        'Content-Type': 'application/json',
    }

    parameter = {
        'limit': 3

    }
    if playlist_id == 'likedsongs':
        # get saved songs/tracks
        saved_info = requests.get(
            'https://api.spotify.com/v1/me/tracks', headers=headers, params=parameter).json()

        # print(saved_info)
        # print(len(saved_info.get('items')))
    else:
        # for playlists tracks
        saved_info = requests.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, params=parameter).json()

    songs = saved_info.get('items')
    for song in songs:
        song_variable = {

            'added_at': song.get('added_at'),
            'artists_url': song.get('track').get('artists')[
                0].get('external_urls').get('spotify'),
            'artists_name': song.get('track').get('artists')[0].get('name'),
            # ms to min
            'duration': ms_to_min(song.get('track').get('duration_ms')),
            'song_name': song.get('track').get('name')

        }
        songs_info.append(song_variable)
        # print(songs_info[0]['added_at'])
    context = {
        'songs_info': songs_info
    }

    return render(request, 'spotify.html', context)


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
