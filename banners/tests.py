from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import BannerForm
from .models import Banner


User = get_user_model()


class PublicBannerTests(TestCase):
    def test_home_displays_only_active_banners_in_position_order(self):
        Banner.objects.create(
            title="Segundo banner",
            description="Segundo mensaje",
            position=20,
            is_active=True,
        )
        Banner.objects.create(
            title="Banner oculto",
            description="No debe aparecer",
            position=0,
            is_active=False,
        )
        Banner.objects.create(
            title="Primer banner",
            description="Primer mensaje",
            position=10,
            is_active=True,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Banner oculto")
        self.assertLess(
            response.content.index(b"Primer banner"),
            response.content.index(b"Segundo banner"),
        )

    def test_banner_form_rejects_unsafe_link_scheme(self):
        form = BannerForm(
            data={
                "title": "Enlace inseguro",
                "description": "Contenido",
                "icon": Banner.Icon.STAR,
                "button_text": "Abrir",
                "button_url": "javascript:alert(1)",
                "position": 0,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("button_url", form.errors)

    def test_rich_description_is_rendered_and_unsafe_html_is_removed(self):
        form = BannerForm(
            data={
                "title": "Contenido enriquecido",
                "description": (
                    "<p>Un texto <strong>importante</strong>.</p>"
                    "<script>alert('unsafe')</script>"
                ),
                "icon": Banner.Icon.BOOK,
                "button_text": "",
                "button_url": "",
                "position": 0,
                "is_active": True,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        banner = form.save()
        self.assertIn("<strong>importante</strong>", banner.description)
        self.assertNotIn("<script", banner.description)

        response = self.client.get(reverse("home"))
        self.assertContains(response, "<strong>importante</strong>", html=True)


class BannerDashboardTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="ClaveSegura-2026!",
        )
        self.banner = Banner.objects.create(
            title="Banner original",
            description="Texto original",
            icon=Banner.Icon.HEART,
            button_text="Conectar",
            button_url="#contacto",
            position=5,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:banner_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_regular_user_cannot_access_banner_management(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(reverse("dashboard:banner_list"))

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_list_banners(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("dashboard:banner_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.banner.title)

    def test_staff_create_page_loads_ckeditor_5(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse("dashboard:banner_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "django_ckeditor_5/dist/bundle.js")
        self.assertContains(response, 'class="django_ckeditor_5"')

    def test_staff_user_can_create_banner(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:banner_create"),
            {
                "title": "Nuevo banner",
                "description": "Un mensaje nuevo",
                "icon": Banner.Icon.CALENDAR,
                "button_text": "Ver fechas",
                "button_url": "#calendario",
                "position": 2,
                "is_active": True,
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:banner_list"),
            fetch_redirect_response=False,
        )
        self.assertTrue(Banner.objects.filter(title="Nuevo banner").exists())

    def test_staff_user_can_update_banner(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:banner_update", args=[self.banner.pk]),
            {
                "title": "Banner actualizado",
                "description": "Texto actualizado",
                "icon": Banner.Icon.BOOK,
                "button_text": "",
                "button_url": "",
                "position": 1,
                "is_active": True,
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:banner_list"),
            fetch_redirect_response=False,
        )
        self.banner.refresh_from_db()
        self.assertEqual(self.banner.title, "Banner actualizado")
        self.assertEqual(self.banner.position, 1)

    def test_staff_user_can_delete_banner_with_post(self):
        self.client.force_login(self.staff_user)

        get_response = self.client.get(
            reverse("dashboard:banner_delete", args=[self.banner.pk])
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertTrue(Banner.objects.filter(pk=self.banner.pk).exists())

        post_response = self.client.post(
            reverse("dashboard:banner_delete", args=[self.banner.pk])
        )
        self.assertRedirects(
            post_response,
            reverse("dashboard:banner_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(Banner.objects.filter(pk=self.banner.pk).exists())
