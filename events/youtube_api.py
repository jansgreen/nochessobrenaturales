import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils.dateparse import parse_datetime


class YouTubeAPIError(Exception):
    pass


class YouTubeAPIConfigurationError(YouTubeAPIError):
    pass


class YouTubeVideoUnavailable(YouTubeAPIError):
    pass


def fetch_youtube_metadata(video_id):
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        raise YouTubeAPIConfigurationError(
            "Agrega YOUTUBE_API_KEY al archivo .env para sincronizar "
            "los datos de YouTube."
        )

    query = urlencode(
        {
            "part": "snippet,status",
            "id": video_id,
            "key": api_key,
            "fields": (
                "items(snippet(title,channelTitle,publishedAt,thumbnails),"
                "status(embeddable,privacyStatus))"
            ),
        }
    )
    request = Request(
        f"https://www.googleapis.com/youtube/v3/videos?{query}",
        headers={"Accept": "application/json"},
    )

    try:
        with urlopen(
            request,
            timeout=settings.YOUTUBE_API_TIMEOUT,
        ) as response:
            payload = json.load(response)
    except (HTTPError, URLError, OSError, TimeoutError, ValueError) as error:
        raise YouTubeAPIError(
            "YouTube no respondió en este momento. El enlace puede "
            "guardarse y sincronizarse después."
        ) from error

    items = payload.get("items", [])
    if not items:
        raise YouTubeVideoUnavailable(
            "YouTube no encontró un video público con este enlace."
        )

    video_data = items[0]
    status = video_data.get("status", {})
    if (
        status.get("embeddable") is False
        or status.get("privacyStatus") == "private"
    ):
        raise YouTubeVideoUnavailable(
            "Este video no permite reproducirse dentro de otros sitios."
        )

    snippet = video_data.get("snippet", {})
    thumbnails = snippet.get("thumbnails", {})
    thumbnail_url = ""
    for size in ("maxres", "standard", "high", "medium", "default"):
        if thumbnails.get(size, {}).get("url"):
            thumbnail_url = thumbnails[size]["url"]
            break

    return {
        "title": snippet.get("title", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "thumbnail_url": thumbnail_url,
        "published_at": parse_datetime(snippet.get("publishedAt", "")),
    }
