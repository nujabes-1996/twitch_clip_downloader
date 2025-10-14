from TwitchApi import TwitchApi
import requests
import json

def get_app_access_token(client_id: str, client_secret: str) -> str:
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    resp = requests.post(url, params=params)
    resp.raise_for_status()
    return resp.json()["access_token"]


if __name__ == "__main__":
    
    with open('../settings.json', 'r') as f:
        config = json.load(f)

    CLIENT_ID = config['twitch']['credentials']['client_id']
    CLIENT_SECRET = config['twitch']['credentials']['client_secret']
    DEFAULT_LIMIT = config['twitch']['settings']['default_limit']
    DEFAULT_PERIOD_DAYS = config['twitch']['settings']['default_period_days']
    OUTPUT_DIR = config['download']['output_dir']
    
    twitch = TwitchApi(CLIENT_ID, CLIENT_SECRET, OUTPUT_DIR)
    game_id = twitch.get_category_id("League of Legends")
    clips = twitch.get_daily_clips_by_category(category_id=game_id, first=10)
    parsed_clips = twitch.parse_clips(clips)
    twitch.download_clips(parsed_clips)
