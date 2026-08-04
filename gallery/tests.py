import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .models import GalleryImage
from .storage import CloudinaryMediaStorage


User = get_user_model()


def uploaded_image(name="gallery-test.png", color=(28, 107, 151)):
    content = BytesIO()
    Image.new("RGB", (120, 90), color).save(content, format="PNG")
    return SimpleUploadedFile(
        name,
        content.getvalue(),
        content_type="image/png",
    )


class TemporaryMediaTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media_root = tempfile.mkdtemp(prefix="gallery-tests-")
        cls.media_override = override_settings(MEDIA_ROOT=cls.media_root)
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(cls.media_root, ignore_errors=True)
        super().tearDownClass()


class PublicGalleryTests(TemporaryMediaTests):
    def create_image(self, index, is_active=True):
        return GalleryImage.objects.create(
            title=f"Recuerdo {index:02d}",
            description=f"Descripción del recuerdo {index}",
            image=uploaded_image(f"recuerdo-{index}.png"),
            alt_text=f"Descripción visual {index}",
            position=index,
            is_active=is_active,
        )

    def test_public_gallery_only_shows_active_images(self):
        visible = self.create_image(1)
        hidden = self.create_image(2, is_active=False)

        response = self.client.get(reverse("gallery:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, visible.title)
        self.assertContains(response, visible.alt_text)
        self.assertNotContains(response, hidden.title)
        self.assertContains(response, 'class="nav-link active"')

    def test_public_gallery_is_paginated_by_twelve_images(self):
        images = [self.create_image(index) for index in range(1, 14)]

        first_page = self.client.get(reverse("gallery:index"))
        second_page = self.client.get(
            reverse("gallery:index"),
            {"pagina": 2},
        )

        self.assertContains(first_page, images[0].title)
        self.assertNotContains(first_page, images[-1].title)
        self.assertContains(first_page, "Página siguiente")
        self.assertContains(second_page, images[-1].title)
        self.assertNotContains(second_page, images[0].title)


class GalleryDashboardTests(TemporaryMediaTests):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="gallery-editor",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="gallery-member",
            password="ClaveSegura-2026!",
        )
        self.gallery_image = GalleryImage.objects.create(
            title="Momento inicial",
            image=uploaded_image("momento-inicial.png"),
            alt_text="Personas reunidas durante el encuentro",
            position=1,
        )

    def image_data(self, **overrides):
        data = {
            "title": "Una noche de fe",
            "description": "Un momento para recordar.",
            "alt_text": "La comunidad reunida en adoración",
            "photographed_on": "2026-07-20",
            "position": 2,
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_gallery_management_requires_staff_access(self):
        anonymous = self.client.get(reverse("dashboard:gallery_image_list"))
        self.assertEqual(anonymous.status_code, 302)

        self.client.force_login(self.regular_user)
        member = self.client.get(reverse("dashboard:gallery_image_list"))
        self.assertEqual(member.status_code, 403)

    def test_staff_user_can_create_gallery_image(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:gallery_image_create"),
            {
                **self.image_data(),
                "image": uploaded_image("nueva-imagen.png"),
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:gallery_image_list"),
            fetch_redirect_response=False,
        )
        created = GalleryImage.objects.exclude(pk=self.gallery_image.pk).get()
        self.assertEqual(created.title, "Una noche de fe")
        self.assertTrue(created.is_active)
        self.assertTrue(created.image.name.startswith("gallery/"))

    def test_staff_user_can_update_without_replacing_file(self):
        original_name = self.gallery_image.image.name
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "dashboard:gallery_image_update",
                args=[self.gallery_image.pk],
            ),
            self.image_data(title="Título actualizado", position=4),
        )

        self.assertRedirects(
            response,
            reverse("dashboard:gallery_image_list"),
            fetch_redirect_response=False,
        )
        self.gallery_image.refresh_from_db()
        self.assertEqual(self.gallery_image.title, "Título actualizado")
        self.assertEqual(self.gallery_image.image.name, original_name)

    def test_deleting_record_also_deletes_its_file(self):
        image_path = self.gallery_image.image.path
        self.assertTrue(self.gallery_image.image.storage.exists(
            self.gallery_image.image.name
        ))
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse(
                "dashboard:gallery_image_delete",
                args=[self.gallery_image.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("dashboard:gallery_image_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(GalleryImage.objects.filter(
            pk=self.gallery_image.pk
        ).exists())
        self.assertFalse(Path(image_path).exists())


class CloudinaryMediaStorageTests(SimpleTestCase):
    @patch("cloudinary.uploader.upload")
    def test_storage_uploads_with_stable_public_id(self, upload):
        upload.return_value = {
            "public_id": "gallery/2026/08/unique-image",
            "format": "webp",
        }
        storage = CloudinaryMediaStorage()

        saved_name = storage._save(
            "gallery/2026/08/unique-image.png",
            BytesIO(b"image-content"),
        )

        self.assertEqual(
            saved_name,
            "gallery/2026/08/unique-image.webp",
        )
        self.assertEqual(
            upload.call_args.kwargs["public_id"],
            "gallery/2026/08/unique-image",
        )

    @patch("cloudinary.utils.cloudinary_url")
    def test_storage_builds_optimized_secure_url(self, cloudinary_url):
        cloudinary_url.return_value = (
            "https://cdn.example.com/gallery/image.webp",
            {},
        )
        storage = CloudinaryMediaStorage()

        url = storage.url("gallery/image.webp")

        self.assertEqual(
            url,
            "https://cdn.example.com/gallery/image.webp",
        )
        self.assertTrue(cloudinary_url.call_args.kwargs["secure"])
        self.assertEqual(
            cloudinary_url.call_args.kwargs["fetch_format"],
            "auto",
        )
        self.assertEqual(
            cloudinary_url.call_args.kwargs["quality"],
            "auto",
        )
