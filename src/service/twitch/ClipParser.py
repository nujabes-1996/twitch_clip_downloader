from typing import List, Dict
from model.ApiParams import ApiParams

class ClipParser:
    @staticmethod
    def parse_clips(clips_response: Dict) -> List[Dict]:
        parsed = []
        for clip in clips_response.get(ApiParams.DATA.value, []):
            parsed.append({
                ApiParams.ID.value: clip.get(ApiParams.ID.value),
                ApiParams.BROADCASTER_NAME.value: clip.get(ApiParams.BROADCASTER_NAME.value),
                ApiParams.VIDEO_ID.value: clip.get(ApiParams.VIDEO_ID.value),
                ApiParams.TITLE.value: clip.get(ApiParams.TITLE.value),
                ApiParams.DURATION.value: clip.get(ApiParams.DURATION.value),
                ApiParams.THUMBNAIL_URL.value: clip.get(ApiParams.THUMBNAIL_URL.value),
            })
        return parsed