import json
from exceptions.AuthenticationError import AuthenticationError
from model.Url import Url
from model.Common import Common
from service.twitch.TwitchAuthenticator import TwitchAuthenticator
from service.twitch.TwitchApiClient import TwitchApiClient
from service.twitch.ClipDownloader import ClipDownloader
from service.twitch.ClipParser import ClipParser
from service.youtube.YoutubeAuthenticator import YoutubeAuthenticator
from service.youtube.YouTubeUploader import YouTubeUploader
import argparse
import os

class Main:
    def __init__(self, config_path: str = 'settings.json', category: str = "League of Legends"):
        self.config_path = config_path
        self.category = category
        self._load_config()
        self.authenticator = TwitchAuthenticator(
            client_id=self.config['twitch']['credentials']['client_id'],
            client_secret=self.config['twitch']['credentials']['client_secret']
        )
        self.api_client = TwitchApiClient(self.authenticator)
        self.parser = ClipParser()
        self.downloader = ClipDownloader()

    def _load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

    def run(self):
        category_id = self.api_client.get_category_id(self.category)
        if not category_id:
            print(f"❌ Catégorie '{self.category}' introuvable.")
            return
        clips_response = self.api_client.get_daily_clips_by_category(category_id)
        clips = self.parser.parse_clips(clips_response)
        if not clips:
            print(f"❌ Aucun clip trouvé pour la catégorie '{self.category}'.")
            return
        self.downloader.download_clips(clips)
        
    def test_youtube_auth(self):
        try:
            # Récupère le chemin du client_secrets.json (depuis la config ou par défaut)
            client_secrets_file = self.config.get("google", {}).get("client_secrets_file", "client_secrets.json")
            # Récupère le chemin du token pickle (depuis la config ou par défaut)
            token_file = self.config.get("google", {}).get("token_file", "token.pickle")
            scopes = [Url.YOUTUBE_GOOGLE_API_READONLY.value]

            # Optionnel : vérifie que le fichier client_secrets.json existe
            if not os.path.exists(client_secrets_file):
                print(f"❌ Le fichier client_secrets.json est introuvable : {client_secrets_file}")
                return

            yt_auth = YoutubeAuthenticator(
                client_secrets_file=client_secrets_file,
                token_file=token_file,
                scopes=scopes
            )
            youtube_service = yt_auth.authenticate()
            if youtube_service:
                print("✅ Connexion à YouTube réussie !")
            else:
                print("❌ Échec de connexion à YouTube.")
        except Exception as e:
            print(f"❌ Erreur lors de la connexion à YouTube : {e}")
            
        def test_youtube_upload():
            try:
                YouTubeUploader.reset_authentication(token_file=Common.TOKEN_FILE.value)

                uploader = YouTubeUploader(
                    client_secrets_file=Common.CLIENT_SECRETS_FILE.value,
                    token_file=Common.TOKEN_FILE.value,
                    scopes=[Url.YOUTUBE_API_FULL.value],
                )

                result = uploader.upload_video(
                    video_file=Common.TEST_VIDEO_FILE.value, 
                    title='Test Upload Script',
                    description='Test d\'upload via script Python',
                    tags=['test', 'script', 'python'],
                    privacy_status='private'
                )

                if result:
                    print("✅ Upload réussi!")

            except FileNotFoundError as e:
                print(f"❌ Fichier manquant: {e}")
            except AuthenticationError as e:
                print(f"❌ Auth YouTube: {e}")
            except Exception as e:
                print(f"❌ Erreur: {e}")
                print("\n🔧 Solutions possibles:")
                print("1. Supprimez token.pickle: rm token.pickle")
                print("2. Vérifiez client_secrets.json")
                print("3. Confirmez que l'API YouTube est activée")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Télécharge les clips Twitch d'une catégorie sur 24h ou teste la connexion YouTube.")
    parser.add_argument('--config', type=str, default='settings.json', help='Chemin du fichier de configuration')
    parser.add_argument('--category', type=str, default='Just Chatting', help='Nom de la catégorie Twitch')
    parser.add_argument('--test-youtube', action='store_true', help='Test de la connexion à YouTube')
    args = parser.parse_args()

    main_app = Main(config_path=args.config, category=args.category)
    
    if args.test_youtube:
        main_app.test_youtube_auth()
    else:
        main_app.run()

