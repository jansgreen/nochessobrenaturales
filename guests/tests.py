import shutil
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from .models import MinistryProfile, ShowcaseCategory, ShowcaseItem


User = get_user_model()


def uploaded_photo(name="showcase-test.png", color=(34, 76, 112)):
    content = BytesIO()
    Image.new("RGB", (320, 400), color).save(content, format="PNG")
    return SimpleUploadedFile(
        name,
        content.getvalue(),
        content_type="image/png",
    )


class TemporaryShowcaseMediaTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tempfile.mkdtemp(prefix="showcase-tests-")
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_root)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.media_root, ignore_errors=True)
        super().tearDownClass()


class PublicShowcaseTests(TemporaryShowcaseMediaTests):
    def create_category(self, title, position, is_active=True):
        return ShowcaseCategory.objects.create(
            title=title,
            headline=f"Encabezado de {title}",
            accent=f"Destacado de {title}",
            description=f"Introducción de {title}",
            position=position,
            is_active=is_active,
        )

    def create_item(self, category, name, position, is_active=True):
        return ShowcaseItem.objects.create(
            category=category,
            name=name,
            role="Detalle breve",
            description=f"Presentación de {name}",
            photo=uploaded_photo(f"{name}.png"),
            alt_text=f"Fotografía de {name}",
            position=position,
            is_active=is_active,
        )

    def test_home_groups_active_items_in_ordered_category_rows(self):
        guests = self.create_category("Invitados especiales", 10)
        locations = self.create_category("Locaciones", 20)
        hidden_category = self.create_category("Fila oculta", 0, is_active=False)
        first_guest = self.create_item(guests, "Invitado primero", 10)
        second_guest = self.create_item(guests, "Invitado segundo", 20)
        location = self.create_item(locations, "Washington Heights", 1)
        hidden_item = self.create_item(locations, "Locación oculta", 0, False)
        self.create_item(hidden_category, "Tarjeta de fila oculta", 1)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'id="destacados-{guests.pk}"')
        self.assertContains(response, f'id="destacados-{locations.pk}"')
        self.assertContains(response, first_guest.name)
        self.assertContains(response, second_guest.name)
        self.assertContains(response, location.name)
        self.assertNotContains(response, hidden_item.name)
        self.assertNotContains(response, hidden_category.title)
        self.assertLess(
            response.content.index(guests.title.encode()),
            response.content.index(locations.title.encode()),
        )
        self.assertLess(
            response.content.index(first_guest.name.encode()),
            response.content.index(second_guest.name.encode()),
        )

    def test_home_uses_selected_language_for_category_and_item(self):
        category = self.create_category("Invitados especiales", 1)
        item = self.create_item(category, "Grace Example", 1)
        ShowcaseCategory.objects.filter(pk=category.pk).update(
            title_en="Locations",
            headline_en="A place to gather.",
            accent_en="Near you.",
            description_en="Find the location that works for you.",
        )
        ShowcaseItem.objects.filter(pk=item.pk).update(
            role_en="Washington Heights",
            description_en="A welcoming place for the whole family.",
            alt_text_en="Front of the Washington Heights location",
        )

        self.client.post(
            reverse("set_language"),
            {"language": "en", "next": reverse("home")},
        )
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Locations")
        self.assertContains(response, "A place to gather.")
        self.assertContains(response, "Washington Heights")
        self.assertContains(response, "A welcoming place for the whole family.")


class PublicMinistryProfileTests(TemporaryShowcaseMediaTests):
    def create_profile(self, name, position, is_active=True):
        return MinistryProfile.objects.create(
            name=name,
            profile_type=MinistryProfile.ProfileType.PASTOR,
            role="Pastor invitado",
            introduction=f"Presentación de {name}.",
            biography=f"Biografía completa de {name}.",
            photo=uploaded_photo(f"{name}.png"),
            alt_text=f"Retrato de {name}",
            position=position,
            is_active=is_active,
        )

    def test_about_lists_only_active_profiles_in_editorial_order(self):
        second = self.create_profile("Pastor Segundo", 20)
        first = self.create_profile("Pastora Primera", 10)
        hidden = self.create_profile("Invitado Oculto", 0, is_active=False)

        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="equipo"')
        self.assertContains(response, first.name)
        self.assertContains(response, second.name)
        self.assertContains(response, first.biography)
        self.assertNotContains(response, hidden.name)
        self.assertLess(
            response.content.index(first.name.encode()),
            response.content.index(second.name.encode()),
        )

    def test_about_uses_selected_language_for_ministry_profile(self):
        profile = self.create_profile("Pastor Example", 1)
        MinistryProfile.objects.filter(pk=profile.pk).update(
            role_en="Guest pastor",
            introduction_en="A life devoted to serving others.",
            biography_en="His ministry shares a message of hope.",
            alt_text_en="Portrait of Pastor Example",
        )

        self.client.post(
            reverse("set_language"),
            {"language": "en", "next": reverse("about")},
        )
        with translation.override("en"):
            response = self.client.get(reverse("about"))

        self.assertContains(response, "Our team")
        self.assertContains(response, "Voices that serve.")
        self.assertContains(response, "Guest pastor")
        self.assertContains(response, "A life devoted to serving others.")
        self.assertContains(response, "His ministry shares a message of hope.")


class MinistryProfileDashboardTests(TemporaryShowcaseMediaTests):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="ministry-editor",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="ministry-member",
            password="ClaveSegura-2026!",
        )
        self.profile = MinistryProfile.objects.create(
            name="Pastor Inicial",
            profile_type=MinistryProfile.ProfileType.PASTOR,
            role="Pastor invitado",
            introduction="Una presentación breve.",
            biography="Una biografía ministerial completa.",
            photo=uploaded_photo("pastor-inicial.png"),
            alt_text="Retrato del Pastor Inicial",
            position=1,
        )

    def profile_data(self, **overrides):
        data = {
            "name": "Pastora Elena Rivera",
            "profile_type": MinistryProfile.ProfileType.GUEST,
            "role": "Conferencista invitada",
            "introduction": "Una vida dedicada a compartir esperanza.",
            "biography": "Su trayectoria refleja una fe activa y compasiva.",
            "alt_text": "Retrato de la Pastora Elena Rivera",
            "position": 2,
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_ministry_management_requires_staff_access(self):
        anonymous = self.client.get(reverse("dashboard:ministry_profile_list"))
        self.assertEqual(anonymous.status_code, 302)

        self.client.force_login(self.regular_user)
        member = self.client.get(reverse("dashboard:ministry_profile_list"))
        self.assertEqual(member.status_code, 403)

    def test_staff_user_can_create_ministry_profile(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:ministry_profile_create"),
            {
                **self.profile_data(),
                "photo": uploaded_photo("pastora-elena.png"),
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:ministry_profile_list"),
            fetch_redirect_response=False,
        )
        created = MinistryProfile.objects.exclude(pk=self.profile.pk).get()
        self.assertEqual(created.name, "Pastora Elena Rivera")
        self.assertTrue(created.photo.name.startswith("ministry/"))

    def test_staff_user_can_update_profile_without_replacing_photo(self):
        original_photo = self.profile.photo.name
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:ministry_profile_update", args=[self.profile.pk]),
            self.profile_data(name="Pastor Actualizado", position=5),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:ministry_profile_list"),
            fetch_redirect_response=False,
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, "Pastor Actualizado")
        self.assertEqual(self.profile.position, 5)
        self.assertEqual(self.profile.photo.name, original_photo)

    def test_deleting_profile_also_deletes_photo(self):
        photo_path = self.profile.photo.path
        self.assertTrue(Path(photo_path).exists())
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:ministry_profile_delete", args=[self.profile.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:ministry_profile_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(MinistryProfile.objects.filter(pk=self.profile.pk).exists())
        self.assertFalse(Path(photo_path).exists())


class ShowcaseDashboardTests(TemporaryShowcaseMediaTests):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="showcase-editor",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="showcase-member",
            password="ClaveSegura-2026!",
        )
        self.category = ShowcaseCategory.objects.create(
            title="Invitados especiales",
            headline="Voces que inspiran.",
            accent="Historias que acercan.",
            description="Personas que compartirán un mensaje de esperanza.",
            position=1,
        )
        self.item = ShowcaseItem.objects.create(
            category=self.category,
            name="Invitado inicial",
            role="Conferencista",
            description="Una breve presentación.",
            photo=uploaded_photo("invitado-inicial.png"),
            alt_text="Retrato del invitado inicial",
            position=1,
        )

    def category_data(self, **overrides):
        data = {
            "title": "Locaciones",
            "headline": "Un lugar para encontrarnos.",
            "accent": "Cerca de ti.",
            "description": "Conoce dónde celebramos cada encuentro.",
            "position": 2,
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def item_data(self, **overrides):
        data = {
            "category": self.category.pk,
            "name": "Washington Heights",
            "role": "Nueva York",
            "description": "Una locación preparada para recibir a toda la familia.",
            "alt_text": "Entrada de la locación de Washington Heights",
            "position": 2,
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_showcase_management_requires_staff_access(self):
        anonymous = self.client.get(reverse("dashboard:showcase_list"))
        self.assertEqual(anonymous.status_code, 302)

        self.client.force_login(self.regular_user)
        member = self.client.get(reverse("dashboard:showcase_list"))
        self.assertEqual(member.status_code, 403)

    def test_staff_user_can_create_category(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:showcase_category_create"),
            self.category_data(),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:showcase_list"),
            fetch_redirect_response=False,
        )
        self.assertTrue(ShowcaseCategory.objects.filter(title="Locaciones").exists())

    def test_staff_user_can_create_item_in_selected_category(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:showcase_item_create"),
            {
                **self.item_data(),
                "photo": uploaded_photo("washington-heights.png"),
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:showcase_list"),
            fetch_redirect_response=False,
        )
        created = ShowcaseItem.objects.exclude(pk=self.item.pk).get()
        self.assertEqual(created.category, self.category)
        self.assertEqual(created.name, "Washington Heights")
        self.assertTrue(created.photo.name.startswith("guests/"))

    def test_staff_user_can_update_item_without_replacing_photo(self):
        original_name = self.item.photo.name
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:showcase_item_update", args=[self.item.pk]),
            self.item_data(name="Nombre actualizado", position=4),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:showcase_list"),
            fetch_redirect_response=False,
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Nombre actualizado")
        self.assertEqual(self.item.position, 4)
        self.assertEqual(self.item.photo.name, original_name)

    def test_deleting_item_also_deletes_photo(self):
        photo_path = self.item.photo.path
        self.assertTrue(Path(photo_path).exists())
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:showcase_item_delete", args=[self.item.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:showcase_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(ShowcaseItem.objects.filter(pk=self.item.pk).exists())
        self.assertFalse(Path(photo_path).exists())
