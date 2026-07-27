from django.utils import timezone

from .models import Event, YouTubeVideo


def get_upcoming_events():
    return Event.objects.filter(
        is_published=True,
        starts_at__gte=timezone.now(),
    ).order_by("starts_at", "id")


def get_next_event():
    upcoming = get_upcoming_events()
    return upcoming.filter(is_featured=True).first() or upcoming.first()


def get_active_videos():
    return YouTubeVideo.objects.filter(is_active=True)


def get_home_videos(limit=3):
    return get_active_videos().filter(show_on_home=True)[:limit]
