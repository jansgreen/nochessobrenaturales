from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="website@example.com",
    CONTACT_RECIPIENT_EMAIL="ministry@example.com",
)
class ContactEmailTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "name": "María Rivera",
            "email": "maria@example.com",
            "topic": "Petición de oración",
            "message": "Por favor, oren por mi familia esta semana.",
            "website": "",
        }

    def test_home_contains_server_contact_form_and_csrf_token(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, "Enviar mensaje")

    def test_home_contains_absolute_social_preview_metadata(self):
        host = "nochesobrenatural-07f49a74f27c.herokuapp.com"

        response = self.client.get(reverse("home"), secure=True, HTTP_HOST=host)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'<meta property="og:url" content="https://{host}/">',
            html=True,
        )
        self.assertContains(
            response,
            (
                '<meta property="og:image" '
                f'content="https://{host}/static/assets/logo.jpeg">'
            ),
            html=True,
        )
        self.assertContains(response, 'name="twitter:card"')

    def test_valid_contact_message_sends_multipart_email(self):
        response = self.client.post(reverse("home"), self.valid_data)

        self.assertRedirects(
            response,
            f"{reverse('home')}#contacto",
            fetch_redirect_response=False,
        )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(
            email.subject,
            "[Noches Sobrenaturales] Petición de oración",
        )
        self.assertEqual(email.to, ["ministry@example.com"])
        self.assertEqual(email.reply_to, ["maria@example.com"])
        self.assertIn("María Rivera", email.body)
        self.assertEqual(email.alternatives[0].mimetype, "text/html")
        self.assertIn("oren por mi familia", email.alternatives[0].content)

    def test_invalid_contact_message_is_not_sent(self):
        data = {**self.valid_data, "message": "Corto"}

        response = self.client.post(reverse("home"), data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(
            response,
            "Escribe un mensaje de al menos 10 caracteres.",
            status_code=400,
        )

    def test_honeypot_submission_is_silently_discarded(self):
        data = {**self.valid_data, "website": "https://spam.example"}

        response = self.client.post(reverse("home"), data)

        self.assertRedirects(
            response,
            f"{reverse('home')}#contacto",
            fetch_redirect_response=False,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_rate_limit_blocks_immediate_second_message(self):
        first_response = self.client.post(reverse("home"), self.valid_data)
        self.assertEqual(first_response.status_code, 302)

        second_response = self.client.post(
            reverse("home"),
            {
                **self.valid_data,
                "topic": "Testimonio",
                "message": "Este es otro mensaje válido para el equipo.",
            },
        )

        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        feedback_response = self.client.get(reverse("home"))
        self.assertContains(
            feedback_response,
            "Espera un momento antes de enviar otro mensaje.",
        )

    def test_html_in_message_is_escaped_in_email(self):
        data = {
            **self.valid_data,
            "message": "Mensaje con <script>alert('x')</script> incluido.",
        }

        self.client.post(reverse("home"), data)

        html_body = mail.outbox[0].alternatives[0].content
        self.assertNotIn("<script>", html_body)
        self.assertIn("&lt;script&gt;", html_body)
