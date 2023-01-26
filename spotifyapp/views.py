from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
import base64
from .utlis import client_auth_url, download_audio, name_to_yt_video_id_generator, update_or_create_tokens, is_user_authenticated

from spotify.settings import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
# send prepare url to frontend so that client can click


# main home page


def home(request):

    context = {

        "client_auth_url": client_auth_url(),

    }

    return render(request, 'home.html', context)


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

    # print('\n\n')
    # print(result)
    # print(state)
    # print('\n\n')
    # print('\n\n')

    # print(result['access_token'])
    # print(result['token_type'])
    # print(result['expires_in'])
    # print(result['refresh_token'])
    # print(result['scope'])

    # print('\n\n')
    # print(result.keys())

    access_token = result['access_token']
    refresh_token = result['refresh_token']
    expires_in = result['expires_in']
    token_type = result['token_type']

    session_id = request.session.session_key
    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create_tokens(session_id, access_token,
                            refresh_token, token_type, expires_in)

    return redirect('home')

    # return render(request, 'spotify.html')


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
