from enum import Enum

class Url(Enum):
    # Twitch URLs
    BASE_API_URL = "https://api.twitch.tv/helix"
    BASE_CLIP_URL = "https://clips.twitch.tv"
    OAUTH2_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    OAUTH2_AUTHORIZE_URL = "https://id.twitch.tv/oauth2/authorize"
    
    GET_USERS_URL = BASE_API_URL + "/users"
    GET_GAMES_URL = BASE_API_URL + "/games"
    GET_CLIPS_URL = BASE_API_URL + "/clips"
    
   # URLs YouTube/Google
    YOUTUBE_GOOGLE_API_READONLY = "https://www.googleapis.com/auth/youtube.readonly"
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    YOUTUBE_TOKEN_URI = "https://oauth2.googleapis.com/token"
    YOUTUBE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
    YOUTUBE_API_FULL = "https://www.googleapis.com/auth/youtube"
