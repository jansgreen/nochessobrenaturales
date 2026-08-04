import re
from urllib.parse import parse_qs, urlsplit

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.formats import date_format
from django.utils import timezone
from django.utils.translation import gettext as _


YOUTUBE_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def validate_event_url(value):
    if value.startswith("#"):
        return
    if value.startswith("/") and not value.startswith("//"):
        return

    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return

    raise ValidationError(
        "Usa una URL http(s), una ruta que comience con / "
        "o una sección que comience con #."
    )


def extract_youtube_video_id(value):
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except (TypeError, ValueError) as error:
        raise ValidationError("Ingresa un enlace válido de YouTube.") from error

    hostname = (parsed.hostname or "").lower().rstrip(".")
    path_parts = [part for part in parsed.path.split("/") if part]
    youtube_hosts = (
        hostname == "youtube.com"
        or hostname.endswith(".youtube.com")
        or hostname == "youtube-nocookie.com"
        or hostname.endswith(".youtube-nocookie.com")
    )

    video_id = ""
    if (
        parsed.scheme.lower() == "https"
        and not parsed.username
        and not parsed.password
        and port in (None, 443)
    ):
        if hostname in {"youtu.be", "www.youtu.be"} and path_parts:
            video_id = path_parts[0]
        elif youtube_hosts:
            if parsed.path.rstrip("/") == "/watch":
                video_id = parse_qs(parsed.query).get("v", [""])[0]
            elif (
                len(path_parts) >= 2
                and path_parts[0] in {"embed", "shorts", "live"}
            ):
                video_id = path_parts[1]

    if not YOUTUBE_VIDEO_ID_PATTERN.fullmatch(video_id):
        raise ValidationError(
            "Usa un enlace HTTPS de un video de YouTube, "
            "YouTube Shorts o youtu.be."
        )

    return video_id


def validate_youtube_url(value):
    extract_youtube_video_id(value)


class Event(models.Model):
    eyebrow = models.CharField(max_length=60, default="Próximo encuentro")
    starts_at = models.DateTimeField()
    admission_text = models.CharField(max_length=80, default="Entrada libre")
    cta_text = models.CharField(max_length=80, default="Reservar mi lugar")
    cta_url = models.CharField(
        max_length=500,
        default="#contacto",
        validators=[validate_event_url],
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("starts_at", "id")
        verbose_name = "evento"
        verbose_name_plural = "eventos"

    def __str__(self):
        return self.full_date_label

    def clean(self):
        super().clean()
        if self.is_featured and not self.is_published:
            raise ValidationError(
                {
                    "is_published": (
                        "El próximo encuentro debe estar publicado."
                    )
                }
            )

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.is_featured:
            Event.objects.exclude(pk=self.pk).update(is_featured=False)
        return super().save(*args, **kwargs)

    @property
    def local_start(self):
        return timezone.localtime(self.starts_at)

    @property
    def day_number(self):
        return f"{self.local_start.day:02d}"

    @property
    def month_name(self):
        return date_format(self.local_start, "F").capitalize()

    @property
    def weekday_name(self):
        return date_format(self.local_start, "l").capitalize()

    @property
    def full_date_label(self):
        return _("%(weekday)s, %(day)s de %(month)s") % {
            "weekday": self.weekday_name,
            "day": self.local_start.day,
            "month": self.month_name.lower(),
        }

    @property
    def time_label(self):
        local_start = self.local_start
        hour = local_start.hour
        display_hour = hour % 12 or 12
        period = "a. m." if hour < 12 else "p. m."
        return f"{display_hour}:{local_start.minute:02d} {period}"

    @property
    def iso_datetime(self):
        return self.local_start.isoformat()


class YouTubeVideo(models.Model):
    youtube_url = models.URLField(
        "enlace de YouTube",
        max_length=500,
        validators=[validate_youtube_url],
    )
    youtube_id = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        editable=False,
    )
    title = models.CharField(max_length=250, blank=True, editable=False)
    channel_title = models.CharField(
        max_length=200,
        blank=True,
        editable=False,
    )
    thumbnail_url = models.URLField(
        max_length=500,
        blank=True,
        editable=False,
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )
    api_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )
    position = models.PositiveIntegerField(default=0)
    show_on_home = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "-published_at", "-created_at")
        verbose_name = "video de YouTube"
        verbose_name_plural = "videos de YouTube"

    def __str__(self):
        return self.display_title

    def clean(self):
        super().clean()
        self.youtube_id = extract_youtube_video_id(self.youtube_url)
        self.youtube_url = self.canonical_url

    def save(self, *args, **kwargs):
        self.youtube_id = extract_youtube_video_id(self.youtube_url)
        self.youtube_url = self.canonical_url
        return super().save(*args, **kwargs)

    def apply_api_metadata(self, metadata):
        self.title = metadata.get("title", "")[:250]
        self.channel_title = metadata.get("channel_title", "")[:200]
        self.thumbnail_url = metadata.get("thumbnail_url", "")[:500]
        self.published_at = metadata.get("published_at")
        self.api_synced_at = timezone.now()

    @property
    def canonical_url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"

    @property
    def display_title(self):
        return self.title or "Revive este encuentro"

    @property
    def display_channel(self):
        return self.channel_title or "Noches Sobrenaturales"

    @property
    def display_thumbnail_url(self):
        return (
            self.thumbnail_url
            or f"https://i.ytimg.com/vi/{self.youtube_id}/hqdefault.jpg"
        )
