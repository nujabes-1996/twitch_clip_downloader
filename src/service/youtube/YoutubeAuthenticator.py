import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from exceptions.AuthenticationError import AuthenticationError
from model.Url import Url

class YoutubeAuthenticator:
    def __init__(
        self,
        client_secrets_file: str = 'client_secrets.json',
        token_file: str = 'token.pickle',
        scopes: list = None,
        service_name: str = 'youtube',
        service_version: str = 'v3'
    ):
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.scopes = scopes if scopes is not None else [Url.YOUTUBE_GOOGLE_API_READONLY.value]
        self.service_name = service_name
        self.service_version = service_version
        self.youtube = None

    def load_credentials(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                return pickle.load(token)
        return None

    def save_credentials(self, creds):
        with open(self.token_file, 'wb') as token:
            pickle.dump(creds, token)

    def refresh_credentials(self, creds):
        print("🔄 Rafraîchissement du token...")
        creds.refresh(Request())
        self.save_credentials(creds)
        return creds

    def create_credentials(self):
        print("🔑 Première authentification...")
        if not os.path.exists(self.client_secrets_file):
            raise AuthenticationError(
                f"❌ Fichier '{self.client_secrets_file}' introuvable !",
                __file__, 29
            )
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
        creds = flow.run_local_server(port=0)
        self.save_credentials(creds)
        print("✅ Authentification réussie !")
        return creds

    def get_valid_credentials(self):
        creds = self.load_credentials()
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            return self.refresh_credentials(creds)
        return self.create_credentials()

    def authenticate(self):
        creds = self.get_valid_credentials()
        self.youtube = build(
            self.service_name,
            self.service_version,
            credentials=creds
        )
        return self.youtube