import os
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from exceptions.AuthenticationError import AuthenticationError
from service.youtube.YoutubeAuthenticator import YoutubeAuthenticator
from model.Url import Url
from model.Common import Common

class YouTubeUploader:
    def __init__(
        self,
        client_secrets_file: str = Common.CLIENT_SECRETS_FILE.value,
        token_file: str = Common.TOKEN_FILE.value,
        scopes: list = None,
        service_name: str = 'youtube',
        service_version: str = 'v3'
    ):
        self.authenticator = YoutubeAuthenticator(
            client_secrets_file=client_secrets_file,
            token_file=token_file,
            scopes=scopes if scopes else [Url.YOUTUBE_API_FULL.value],
            service_name=service_name,
            service_version=service_version
        )
        self.youtube = self._authenticate_and_verify()

    def _authenticate_and_verify(self):
        """Authentifie et vérifie les permissions d'upload"""
        youtube = self.authenticator.authenticate()
        self._verify_permissions(youtube)
        return youtube

    def _verify_permissions(self, youtube):
        """Vérifie les permissions d'upload sur YouTube"""
        try:
            print("🔍 Vérification des permissions d'upload...")
            youtube.channels().list(part='snippet', mine=True).execute()
            print("✅ Permissions YouTube confirmées")
        except HttpError as e:
            if e.resp.status == 403:
                print("❌ Permissions insuffisantes!")
                print("💡 Supprimez le fichier token.pickle et relancez le script")
                raise
            else:
                raise

    def _prepare_metadata(self, title, description="", tags=None, category_id="22", privacy_status="private"):
        """Prépare les métadonnées de la vidéo"""
        if tags is None:
            tags = []
        return {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

    def _create_media_upload(self, video_file):
        """Crée l'objet MediaFileUpload"""
        return MediaFileUpload(
            video_file,
            chunksize=-1,
            resumable=True
        )

    def upload_video(
        self, video_file, title, description="", tags=None,
        category_id="22", privacy_status="private"
    ):
        """Upload une vidéo sur YouTube avec gestion d'erreurs améliorée"""
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Fichier vidéo non trouvé: {video_file}")

        body = self._prepare_metadata(title, description, tags, category_id, privacy_status)
        media = self._create_media_upload(video_file)

        print(f"📁 Préparation de l'upload: {video_file}")
        print(f"📝 Titre: {title}")
        print(f"🔒 Confidentialité: {privacy_status}")

        try:
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            response = self._resumable_upload(insert_request)
            return response

        except HttpError as e:
            if e.resp.status == 403:
                print("❌ ERREUR 403: Permissions insuffisantes!")
                print("🔧 Solutions:")
                print("   1. Supprimez le fichier 'token.pickle'")
                print("   2. Relancez le script pour réauthentification")
                print("   3. Vérifiez que l'API YouTube Data v3 est activée")
            else:
                print(f'❌ Erreur HTTP lors de l\'upload: {e}')
            raise

    def _resumable_upload(self, insert_request):
        """Gère l'upload resumable avec meilleure lisibilité et moins de complexité"""
        response = None
        retry = 0
        max_retries = 3

        while response is None:
            try:
                print("📤 Upload en cours...")
                status, response = insert_request.next_chunk()
                self._print_progress(status)
                if response is not None:
                    self._handle_upload_response(response)
            except HttpError as e:
                if self._is_retriable_error(e) and retry < max_retries:
                    retry += 1
                    print(f"⚠️  Erreur serveur récupérable: {e} (tentative {retry}/{max_retries})")
                else:
                    print(f"❌ Erreur HTTP non récupérable: {e}")
                    raise
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
                raise
        return response

    def _print_progress(self, status):
        if status:
            print(f"📊 Progression: {int(status.progress() * 100)}%")

    def _handle_upload_response(self, response):
        if 'id' in response:
            video_id = response['id']
            print("🎉 Upload terminé avec succès!")
            print(f"🆔 ID vidéo: {video_id}")
            print(f"🔗 URL: https://www.youtube.com/watch?v={video_id}")
            print(f"🔗 Studio: https://studio.youtube.com/video/{video_id}/edit")
        else:
            raise AuthenticationError(f'Upload échoué: {response}')

    def _is_retriable_error(self, error):
        return isinstance(error, HttpError) and error.resp.status in [500, 502, 503, 504]

    @staticmethod
    def reset_authentication(token_file=Common.TOKEN_FILE.value):
        """Supprime les tokens pour forcer une réauthentification"""
        if os.path.exists(token_file):
            os.remove(token_file)
            print("🗑️  Token supprimé, réauthentification nécessaire")
        else:
            print("ℹ️  Aucun token à supprimer")
