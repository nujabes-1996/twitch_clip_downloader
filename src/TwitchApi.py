from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import requests
import re
import os
from exceptions.AuthenticationError import AuthenticationError

class TwitchApi:
    def __init__(self, client_id: str, client_secret: str, output_dir: str = "downloads"):
        """
        Initialise l'API Twitch
        
        Args:
            client_id: ID client de votre app Twitch
            client_secret: Secret client de votre app Twitch
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.headers = {}
        self._authenticate()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _authenticate(self):
        """Authentification OAuth2 avec Twitch"""
        auth_url = "https://id.twitch.tv/oauth2/token"
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
                44
            )
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Effectue une requête à l'API Twitch avec gestion d'erreurs"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API: {e}")
            return {}
    
    def get_broadcaster_id(self, username: str) -> Optional[str]:
        """Récupère l'ID d'un broadcaster à partir de son nom d'utilisateur"""
        url = "https://api.twitch.tv/helix/users"
        params = {'login': username}
        
        data = self._make_request(url, params)
        if data.get('data'):
            return data['data'][0]['id']
        return None
    
    def get_category_id(self, game_name: str) -> Optional[str]:
        """Récupère l'ID d'un jeu à partir de son nom"""
        url = "https://api.twitch.tv/helix/games"
        params = {'name': game_name}
        
        data = self._make_request(url, params)
        if data.get('data'):
            return data['data'][0]['id']
        return None

    def get_daily_clips_by_category(
        self,
        category_id: str,
        first: int = 20,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict:
        """
        Récupère les clips d'une catégorie créés au cours des dernières 24h

        Args:
            category_id: ID de la catégorie (jeu)
            language: Filtrer par langue (ex: 'fr')
            sort: Méthode de tri ('time' ou 'views')
            first: Nombre d’items à retourner (1-100, défaut 20)
            after: Curseur pagination (page suivante)
            before: Curseur pagination (page précédente)

        Returns:
            Dict: Résultats de l’API contenant les clips
        """
        url = "https://api.twitch.tv/helix/clips"
        ended_at = datetime.now(timezone.utc)
        started_at = ended_at - timedelta(days=1)

        params = {
            "game_id": category_id,
            "first": first,
            "started_at": self.to_rfc3339(started_at),
            "ended_at": self.to_rfc3339(ended_at),
        }

        if after:
            params["after"] = after
        if before:
            params["before"] = before

        data = self._make_request(url, params)

        return data

    def to_rfc3339(self, dt: datetime) -> str:
            return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


    def parse_clips(self, clips_response: Dict) -> List[Dict]:
        """
        Parse la réponse API Twitch pour ne garder que les infos essentielles
        
        Args:
            clips_response (Dict): Réponse brute de l'API Twitch
        
        Returns:
            List[Dict]: Liste des clips formatés
        """
        parsed = []
        for clip in clips_response.get("data", []):
            parsed.append({
                "id": clip.get("id"),
                "broadcaster_name": clip.get("broadcaster_name"),
                "video_id": clip.get("video_id"),
                "title": clip.get("title"),
                "duration": clip.get("duration"),
                "thumbnail_url": clip.get("thumbnail_url"),
            })
        return parsed
    
    def _sanitize_title(self, title: str) -> str:
        """Nettoie le titre pour l'utiliser comme nom de fichier"""
        return re.sub(r"[^a-zA-Z0-9-_ ]", "", title).strip()[:50] or "clip"

    def _get_video_url(self, thumbnail_url: str) -> str:
        """Construit l'URL .mp4 à partir du thumbnail_url"""
        return thumbnail_url.split("-preview-")[0] + ".mp4"

    def download_clip(self, clip_info: dict) -> str:
        """Télécharge un clip à partir de son objet JSON (Helix API)"""
        clip_title = self._sanitize_title(clip_info["title"])
        file_name = f"{clip_title}_{clip_info['id']}.mp4"
        file_path = os.path.join(self.output_dir, file_name)

        video_url = self._get_video_url(clip_info["thumbnail_url"])

        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return file_path

    def download_clips(self, clips_data: list) -> list:
        """Télécharge une liste de clips (JSON Helix API)"""
        results = []
        for clip in clips_data:
            try:
                path = self.download_clip(clip)
                results.append(path)
                print(f"✅ Clip téléchargé : {path}")
            except Exception as e:
                print(f"❌ Erreur sur {clip['id']} : {e}")
        return results
