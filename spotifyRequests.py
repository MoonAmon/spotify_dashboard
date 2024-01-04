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

    URL = dict(track='https://api.spotify.com/v1/tracks/', album='https://api.spotify.com/v1/albums/',
               artist='https://api.spotify.com/v1/artists/', tracks='https://api.spotify.com/v1/tracks?ids=', me='https://api.spotify.com/v1/me')

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
        if isinstance(uri, str):
            url = self.URL['track'] + uri
            response = requests.get(url, headers=self.headers)
            return response.json()
        elif isinstance(uri, list):
            concatenated_uris = []
            for i in range(0, len(uri), 50):
                sliced_uris = uri[i:i+50]
                concatenated_uris.append(','.join(sliced_uris))
            responses = []
            for uri_group in tqdm(concatenated_uris):
                response = requests.get(self.URL['tracks'] + uri_group, headers=self.headers)
                responses.append(response)
        return [res.json() for res in responses]

    def get_info(self):
        response = requests.get(self.URL['me'], headers=self.headers)
        return response


def get_uri_ids(dataframe_main, option):
    uri_list = []
    for raw_uri in dataframe_main[f'spotify_{option}_uri']:
        uri_list.append(raw_uri[14:])

    return uri_list


def get_df_tracks(list_response):
    df = pd.concat([pd.json_normalize(track) for response in list_response for track in response['tracks']])

    return df


