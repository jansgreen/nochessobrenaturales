from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class RegistrationTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear mi cuenta")

    def test_registration_creates_and_authenticates_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "maria",
                "email": "Maria@Example.com",
                "password1": "FeSegura-2026!",
                "password2": "FeSegura-2026!",
            },
        )

        self.assertRedirects(
            response, reverse("dashboard:home"), fetch_redirect_response=False
        )
        user = User.objects.get(username="maria")
        self.assertEqual(user.email, "maria@example.com")
        self.assertEqual(self.client.session.get("_auth_user_id"), str(user.pk))

    def test_registration_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="persona@example.com",
            password="FeSegura-2026!",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-user",
                "email": "PERSONA@example.com",
                "password1": "OtraClave-2026!",
                "password2": "OtraClave-2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Ya existe una cuenta registrada con este correo."
        )
        self.assertFalse(User.objects.filter(username="new-user").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="juan",
            email="juan@example.com",
            password="FeSegura-2026!",
        )

    def test_login_authenticates_user(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "juan", "password": "FeSegura-2026!"},
        )

        self.assertRedirects(
            response, reverse("dashboard:home"), fetch_redirect_response=False
        )
        self.assertEqual(
            self.client.session.get("_auth_user_id"), str(self.user.pk)
        )

    def test_login_rejects_unsafe_next_url(self):
        response = self.client.post(
            f"{reverse('accounts:login')}?next=https://example.net/steal",
            {"username": "juan", "password": "FeSegura-2026!"},
        )

        self.assertRedirects(
            response, reverse("dashboard:home"), fetch_redirect_response=False
        )

    def test_logout_requires_post_and_ends_session(self):
        self.client.force_login(self.user)

        get_response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            post_response, reverse("accounts:login"), fetch_redirect_response=False
        )
        self.assertNotIn("_auth_user_id", self.client.session)


class DashboardAccessTests(TestCase):
    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard:home"))

        expected = (
            f"{reverse('accounts:login')}?next={reverse('dashboard:home')}"
        )
        self.assertRedirects(response, expected, fetch_redirect_response=False)

