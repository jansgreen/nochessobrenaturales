from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import YouTubeVideoForm
from .models import Event, YouTubeVideo, extract_youtube_video_id
from .selectors import get_next_event, get_upcoming_events
from .youtube_api import YouTubeVideoUnavailable


User = get_user_model()


def future_local_datetime(days=10, hour=19):
    value = timezone.localtime(timezone.now() + timedelta(days=days))
    return value.replace(hour=hour, minute=0, second=0, microsecond=0)


class EventSelectorTests(TestCase):
    def setUp(self):
        Event.objects.all().delete()

    def test_featured_future_event_is_selected_as_next(self):
        Event.objects.create(starts_at=future_local_datetime(days=5))
        featured = Event.objects.create(
            starts_at=future_local_datetime(days=12),
            is_featured=True,
        )

        self.assertEqual(get_next_event(), featured)

    def test_selector_falls_back_to_earliest_published_future_event(self):
        later = Event.objects.create(starts_at=future_local_datetime(days=20))
        earlier = Event.objects.create(starts_at=future_local_datetime(days=8))
        Event.objects.create(
            starts_at=future_local_datetime(days=4),
            is_published=False,
        )
        Event.objects.create(starts_at=timezone.now() - timedelta(days=1))

        self.assertEqual(get_next_event(), earlier)
        self.assertEqual(list(get_upcoming_events()), [earlier, later])

    def test_event_exposes_spanish_card_fields(self):
        event = Event.objects.create(
            starts_at=future_local_datetime(days=10, hour=19),
        )

        self.assertRegex(event.day_number, r"^\d{2}$")
        self.assertTrue(event.month_name)
        self.assertIn(" de ", event.full_date_label)
        self.assertEqual(event.time_label, "7:00 p. m.")
        self.assertRegex(event.iso_datetime, r"[+-]\d{2}:\d{2}$")


class EventDashboardTests(TestCase):
    def setUp(self):
        Event.objects.all().delete()
        self.staff_user = User.objects.create_user(
            username="event-editor",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="event-member",
            password="ClaveSegura-2026!",
        )
        self.event = Event.objects.create(
            starts_at=future_local_datetime(days=10),
            is_featured=True,
        )

    def event_data(self, **overrides):
        data = {
            "eyebrow": "Próximo encuentro",
            "starts_at": future_local_datetime(days=30).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "admission_text": "Entrada libre",
            "cta_text": "Reservar mi lugar",
            "cta_url": "#contacto",
            "is_published": "on",
        }
        data.update(overrides)
        return data

    def test_regular_user_cannot_manage_events(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(reverse("dashboard:event_list"))

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_create_and_feature_event(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:event_create"),
            self.event_data(is_featured="on"),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:event_list"),
            fetch_redirect_response=False,
        )
        created = Event.objects.exclude(pk=self.event.pk).get()
        self.assertTrue(created.is_featured)
        self.event.refresh_from_db()
        self.assertFalse(self.event.is_featured)

    def test_staff_user_can_update_event_card_fields(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:event_update", args=[self.event.pk]),
            self.event_data(
                eyebrow="Noche especial",
                admission_text="Cupos limitados",
                cta_text="Inscribirme",
                cta_url="/accounts/registro/",
                is_featured="on",
            ),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:event_list"),
            fetch_redirect_response=False,
        )
        self.event.refresh_from_db()
        self.assertEqual(self.event.eyebrow, "Noche especial")
        self.assertEqual(self.event.admission_text, "Cupos limitados")
        self.assertEqual(self.event.cta_text, "Inscribirme")

    def test_staff_can_select_existing_event_as_next(self):
        other_event = Event.objects.create(
            starts_at=future_local_datetime(days=20),
        )
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:event_feature", args=[other_event.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:event_list"),
            fetch_redirect_response=False,
        )
        other_event.refresh_from_db()
        self.event.refresh_from_db()
        self.assertTrue(other_event.is_featured)
        self.assertTrue(other_event.is_published)
        self.assertFalse(self.event.is_featured)

    def test_staff_can_delete_event(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:event_delete", args=[self.event.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:event_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())

    def test_event_form_rejects_past_date(self):
        self.client.force_login(self.staff_user)
        past_value = timezone.localtime(
            timezone.now() - timedelta(days=1)
        ).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(
            reverse("dashboard:event_create"),
            self.event_data(starts_at=past_value),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecciona una fecha y hora futuras.")


class PublicEventTests(TestCase):
    def setUp(self):
        Event.objects.all().delete()

    def test_featured_event_populates_spotlight_and_calendar(self):
        event = Event.objects.create(
            eyebrow="Encuentro especial",
            starts_at=future_local_datetime(days=15, hour=20),
            admission_text="Entrada con registro",
            cta_text="Registrarme",
            cta_url="/accounts/registro/",
            is_featured=True,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Encuentro especial")
        self.assertContains(response, event.full_date_label)
        self.assertContains(response, "8:00 p. m.")
        self.assertContains(response, "Entrada con registro")
        self.assertContains(response, 'data-cta-text="Registrarme"')
        self.assertContains(response, event.iso_datetime)

    def test_unpublished_event_is_not_rendered(self):
        hidden = Event.objects.create(
            eyebrow="Evento privado",
            starts_at=future_local_datetime(days=10),
            is_published=False,
        )

        response = self.client.get(reverse("home"))

        self.assertNotContains(response, hidden.eyebrow)
        self.assertContains(
            response,
            "Publicaremos la próxima fecha muy pronto.",
        )


class YouTubeVideoValidationTests(TestCase):
    def test_supported_youtube_links_return_the_video_id(self):
        video_id = "dQw4w9WgXcQ"
        links = (
            f"https://www.youtube.com/watch?v={video_id}",
            f"https://youtu.be/{video_id}",
            f"https://www.youtube.com/shorts/{video_id}",
            f"https://www.youtube.com/live/{video_id}",
            f"https://www.youtube-nocookie.com/embed/{video_id}",
        )

        for link in links:
            with self.subTest(link=link):
                self.assertEqual(extract_youtube_video_id(link), video_id)

    def test_invalid_or_deceptive_youtube_links_are_rejected(self):
        links = (
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com.example.org/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/channel/dQw4w9WgXcQ",
            "https://example.com/watch?v=dQw4w9WgXcQ",
        )

        for link in links:
            with self.subTest(link=link):
                with self.assertRaises(ValidationError):
                    extract_youtube_video_id(link)

    def test_form_rejects_a_duplicate_video(self):
        YouTubeVideo.objects.create(
            youtube_url="https://youtu.be/dQw4w9WgXcQ"
        )

        form = YouTubeVideoForm(
            data={
                "youtube_url": (
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                ),
                "position": 0,
                "show_on_home": True,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("youtube_url", form.errors)


class YouTubeVideoDashboardTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="video-editor",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="video-member",
            password="ClaveSegura-2026!",
        )

    def video_data(self, **overrides):
        data = {
            "youtube_url": "https://youtu.be/dQw4w9WgXcQ",
            "position": 1,
            "show_on_home": "on",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_video_management_requires_staff_access(self):
        anonymous_response = self.client.get(
            reverse("dashboard:youtube_video_list")
        )
        self.assertEqual(anonymous_response.status_code, 302)

        self.client.force_login(self.regular_user)
        member_response = self.client.get(
            reverse("dashboard:youtube_video_list")
        )
        self.assertEqual(member_response.status_code, 403)

    @override_settings(YOUTUBE_API_KEY="")
    def test_staff_can_add_video_before_api_key_is_configured(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:youtube_video_create"),
            self.video_data(),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:youtube_video_list"),
            fetch_redirect_response=False,
        )
        video = YouTubeVideo.objects.get()
        self.assertEqual(video.youtube_id, "dQw4w9WgXcQ")
        self.assertEqual(
            video.youtube_url,
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        self.assertTrue(video.show_on_home)
        self.assertTrue(video.is_active)

    @override_settings(YOUTUBE_API_KEY="test-api-key")
    @patch("dashboard.views.fetch_youtube_metadata")
    def test_api_metadata_is_saved_automatically(self, fetch_metadata):
        published_at = timezone.now() - timedelta(days=5)
        fetch_metadata.return_value = {
            "title": "Una noche de fe",
            "channel_title": "Iglesia Milagros Hoy",
            "thumbnail_url": "https://i.ytimg.com/vi/test/maxres.jpg",
            "published_at": published_at,
        }
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:youtube_video_create"),
            self.video_data(),
        )

        self.assertEqual(response.status_code, 302)
        video = YouTubeVideo.objects.get()
        self.assertEqual(video.title, "Una noche de fe")
        self.assertEqual(video.channel_title, "Iglesia Milagros Hoy")
        self.assertEqual(video.published_at, published_at)
        self.assertIsNotNone(video.api_synced_at)

    @override_settings(YOUTUBE_API_KEY="test-api-key")
    @patch("dashboard.views.fetch_youtube_metadata")
    def test_non_embeddable_video_is_not_saved(self, fetch_metadata):
        fetch_metadata.side_effect = YouTubeVideoUnavailable(
            "Este video no permite reproducirse dentro de otros sitios."
        )
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:youtube_video_create"),
            self.video_data(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Este video no permite reproducirse dentro de otros sitios.",
        )
        self.assertFalse(YouTubeVideo.objects.exists())


class PublicYouTubeGalleryTests(TestCase):
    def setUp(self):
        self.home_video = YouTubeVideo.objects.create(
            youtube_url="https://youtu.be/dQw4w9WgXcQ",
            title="Video destacado",
            channel_title="Canal principal",
            position=1,
            show_on_home=True,
            is_active=True,
        )
        self.gallery_video = YouTubeVideo.objects.create(
            youtube_url="https://youtu.be/M7lc1UVf-VE",
            title="Solo en la galería",
            position=2,
            show_on_home=False,
            is_active=True,
        )
        self.hidden_video = YouTubeVideo.objects.create(
            youtube_url="https://youtu.be/aqz-KE-bpKQ",
            title="Video oculto",
            position=3,
            show_on_home=True,
            is_active=False,
        )

    def test_home_shows_only_active_featured_videos(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, self.home_video.title)
        self.assertNotContains(response, self.gallery_video.title)
        self.assertNotContains(response, self.hidden_video.title)
        self.assertContains(
            response,
            f'data-youtube-video="{self.home_video.youtube_id}"',
        )

    def test_events_page_shows_active_gallery_and_navigation_tab(self):
        response = self.client.get(reverse("events:gallery"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.home_video.title)
        self.assertContains(response, self.gallery_video.title)
        self.assertNotContains(response, self.hidden_video.title)
        self.assertContains(response, "Eventos que dejan")
        self.assertContains(
            response,
            'class="nav-link active" href="/eventos/"',
        )

    def test_home_limits_showcase_to_three_videos(self):
        for position, video_id in (
            (4, "ysz5S6PUM-U"),
            (5, "ScMzIvxBSi4"),
            (6, "jNQXAC9IVRw"),
        ):
            YouTubeVideo.objects.create(
                youtube_url=f"https://youtu.be/{video_id}",
                title=f"Video número {position}",
                position=position,
                show_on_home=True,
                is_active=True,
            )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Video número 4")
        self.assertContains(response, "Video número 5")
        self.assertNotContains(response, "Video número 6")
