import requests
import re
import os
from model.ApiParams import ApiParams
from model.Common import Common

class ClipDownloader:
    def __init__(self, output_dir: str = Common.DOWNLOADS_DIR.value):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def sanitize_title(self, title: str) -> str:
        return re.sub(r"[^a-zA-Z0-9-_ ]", "", title).strip()[:50] or "clip"

    def get_video_url(self, thumbnail_url: str) -> str:
        return thumbnail_url.split("-preview-")[0] + ".mp4"

    def download_clip(self, clip_info: dict) -> str:
        clip_title = self.sanitize_title(clip_info[ApiParams.TITLE.value])
        file_name = f"{clip_title}_{clip_info[ApiParams.ID.value]}.mp4"
        file_path = os.path.join(self.output_dir, file_name)
        video_url = self.get_video_url(clip_info[ApiParams.THUMBNAIL_URL.value])
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return file_path

    def download_clips(self, clips_data: list) -> list:
        results = []
        for clip in clips_data:
            try:
                path = self.download_clip(clip)
                results.append(path)
                print(f"✅ Clip téléchargé : {path}")
            except Exception as e:
                print(f"❌ Erreur sur {clip[ApiParams.ID.value]} : {e}")
        return results