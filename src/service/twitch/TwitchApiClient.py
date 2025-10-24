from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import requests
from service.twitch.TwitchAuthenticator import TwitchAuthenticator
from model.Url import Url
from model.ApiParams import ApiParams

class TwitchApiClient:
    def __init__(self, authenticator: TwitchAuthenticator):
        self.authenticator = authenticator
        if not self.authenticator.headers:
            self.authenticator.authenticate()

    def make_request(self, url: str, params: Dict = None) -> Dict:
        try:
            response = requests.get(url, headers=self.authenticator.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API: {e}")
            return {}

    def get_broadcaster_id(self, username: str) -> Optional[str]:
        url = Url.GET_USERS_URL.value
        params = {'login': username}
        data = self.make_request(url, params)
        if data.get(ApiParams.DATA.value):
            return data[ApiParams.DATA.value][0][ApiParams.ID.value]
        return None

    def get_category_id(self, game_name: str) -> Optional[str]:
        url = Url.GET_GAMES_URL.value
        params = {ApiParams.NAME.value: game_name}
        data = self.make_request(url, params)
        if data.get(ApiParams.DATA.value):
            return data[ApiParams.DATA.value][0][ApiParams.ID.value]
        return None

    def get_daily_clips_by_category(
        self,
        category_id: str,
        first: int = 2,
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict:
        url = Url.GET_CLIPS_URL.value
        ended_at = datetime.now(timezone.utc)
        started_at = ended_at - timedelta(days=1)
        params = {
            ApiParams.GAME_ID.value: category_id,
            ApiParams.FIRST.value: first,
            ApiParams.STARTED_AT.value: self.to_rfc3339(started_at),
            ApiParams.ENDED_AT.value: self.to_rfc3339(ended_at),
        }
        if after:
            params[ApiParams.AFTER.value] = after
        if before:
            params[ApiParams.BEFORE.value] = before
        return self.make_request(url, params)

    @staticmethod
    def to_rfc3339(dt: datetime) -> str:
        return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")