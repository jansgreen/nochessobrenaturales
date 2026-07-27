from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import DonationSettings


User = get_user_model()


class DonationSettingsValidationTests(TestCase):
    def test_official_paypal_and_paypal_me_links_are_accepted(self):
        valid_links = (
            "https://www.paypal.com/donate/?hosted_button_id=ABC123",
            "https://paypal.me/iglesiamilagroshoy",
        )

        for link in valid_links:
            with self.subTest(link=link):
                settings = DonationSettings(paypal_url=link)
                settings.full_clean()

    def test_non_paypal_or_insecure_links_are_rejected(self):
        invalid_links = (
            "https://paypal.com.example.org/donar",
            "https://evilpaypal.com/donar",
            "http://paypal.me/iglesia",
        )

        for link in invalid_links:
            with self.subTest(link=link):
                with self.assertRaises(ValidationError):
                    DonationSettings(paypal_url=link).full_clean()


class DonationDashboardTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="donation-editor",
            password="ClaveSegura-2026!",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="donation-member",
            password="ClaveSegura-2026!",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("dashboard:donation_settings")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_regular_user_cannot_manage_donations(self):
        self.client.force_login(self.regular_user)

        response = self.client.get(
            reverse("dashboard:donation_settings")
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_save_only_one_paypal_configuration(self):
        self.client.force_login(self.staff_user)
        link = "https://www.paypal.com/donate/?hosted_button_id=ABC123"

        response = self.client.post(
            reverse("dashboard:donation_settings"),
            {"paypal_url": link},
        )

        self.assertRedirects(
            response,
            reverse("dashboard:donation_settings"),
            fetch_redirect_response=False,
        )
        self.assertEqual(DonationSettings.objects.count(), 1)
        self.assertEqual(DonationSettings.objects.get(pk=1).paypal_url, link)

        self.client.post(
            reverse("dashboard:donation_settings"),
            {"paypal_url": "https://paypal.me/iglesiamilagroshoy"},
        )
        self.assertEqual(DonationSettings.objects.count(), 1)

    def test_dashboard_rejects_non_paypal_link(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(
            reverse("dashboard:donation_settings"),
            {"paypal_url": "https://example.com/donar"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Usa un enlace seguro de paypal.com o paypal.me.",
        )
        self.assertFalse(DonationSettings.objects.exists())


class PublicDonationButtonTests(TestCase):
    def test_button_is_hidden_without_a_configured_link(self):
        response = self.client.get(reverse("home"))

        self.assertNotContains(response, ">Donaciones</a>")

    def test_button_uses_configured_paypal_link(self):
        link = "https://paypal.me/iglesiamilagroshoy"
        DonationSettings.objects.create(paypal_url=link)

        response = self.client.get(reverse("home"))

        self.assertContains(response, f'href="{link}"')
        self.assertContains(response, ">Donaciones</a>")
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener noreferrer"')

