import requests
from exceptions.AuthenticationError import AuthenticationError
from model.Url import Url

class TwitchAuthenticator:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.headers = None

    def authenticate(self):
        auth_url = Url.OAUTH2_TOKEN_URL.value
        auth_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(auth_url, params=auth_params)
        if response.status_code == 200:
            auth_data = response.json()
            self.access_token = auth_data['access_token']
            self.headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}'
            }
            print("✅ Authentification réussie")
        else:
            raise AuthenticationError(
                f"❌ Erreur authentification: {response.status_code}", 
                __file__, 
                19
            )