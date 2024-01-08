import requests
import base64
import pandas as pd
from tqdm import tqdm
import time


class SpotifyCredentials:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.set_access_token()
        self.headers = self.set_headers()

    def set_access_token(self):
        credentials = base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode('utf-8')).decode('utf-8')

        headers = {
            'Authorization': f'Basic {credentials}',
        }

        data = {
            'grant_type': 'client_credentials',
        }

        response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
        return response.json().get('access_token')

    def set_headers(self):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        return headers


class SpotifyRequests(SpotifyCredentials):

    URL = {'track': 'https://api.spotify.com/v1/tracks/',
           'album': 'https://api.spotify.com/v1/albums/',
           'artist': 'https://api.spotify.com/v1/artists/',
           'tracks': 'https://api.spotify.com/v1/tracks?ids=',
           'me': 'https://api.spotify.com/v1/me',
           'audio_features': 'https://api.spotify.com/v1/audio-features?ids='}

    def __init__(self, client_id, client_secret):
        super().__init__(client_id, client_secret)

    def get_album(self, uri):
        url = self.URL['album'] + uri
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_artist(self, uri):
        url = self.URL['artist'] + uri
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_track(self, uri):
        url = self.URL['track'] + uri
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_info(self):
        url = self.URL['me']
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_several_tracks(self, uri_group, retries=5, backoff_factor=0.3):
        response_list = []
        for n in range(retries):
            try:
                for i in range(0, len(uri_group), 50):
                    uri_string = ','.join(uri_group[i:i+50])
                    url = self.URL['tracks'] + uri_string
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        response_list.extend(response.json()['tracks'])
                return response_list
            except requests.exceptions.RequestException as e:
                if n == retries - 1:
                    raise
                else:
                    print(f"Request failed, retrying in {backoff_factor * (2 ** n)} seconds...")
                    time.sleep(backoff_factor * (2 ** n))

    def get_several_tracks_features(self, uri_group, retries=5, backoff_factor=0.3):
        response_list = []
        for n in range(retries):
            try:
                for i in range(0, len(uri_group), 100):
                    uri_string = ','.join(uri_group[i:i + 100])
                    url = self.URL['audio_features'] + uri_string
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        response_list.extend(response.json()['audio_features'])
                return response_list
            except requests.exceptions.RequestException as e:
                if n == retries - 1:
                    raise
                else:
                    print(f"Request failed, retrying in {backoff_factor * (2 ** n)} seconds...")
                    time.sleep(backoff_factor * (2 ** n))


def get_uri_ids(dataframe_main, option):
    uri_list = []
    for raw_uri in dataframe_main[f'spotify_{option}_uri']:
        uri_list.append(raw_uri[14:])

    return uri_list


def get_df_tracks(list_response):
    df = pd.concat([pd.json_normalize(track) for response in list_response for track in response['tracks']])

    return df


