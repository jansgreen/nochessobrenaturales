from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from banners.models import Banner


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

    def test_home_contains_free_bible_and_guest_benefits(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solicita Tu")
        self.assertContains(response, "Biblia Gratis.")
        self.assertContains(response, "Estacionamiento valet gratis")
        self.assertContains(response, "Comida o refrigerios gratis")
        self.assertContains(response, "Regalos gratis")
        self.assertContains(response, "Desde El Bronx hasta Washington Heights.")
        self.assertContains(response, 'data-topic="Biblia gratis"', count=2)

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


class AboutPageTests(TestCase):
    def test_about_page_contains_pastor_biography_and_ministry_details(self):
        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pastor Richie Ramos")
        self.assertContains(
            response,
            '<figcaption class="about-identity-caption">Pastor Richie Ramos</figcaption>',
            html=True,
        )
        self.assertNotContains(response, 'class="about-identity-copy"')
        self.assertNotContains(response, '<span aria-hidden="true">RR</span>')
        self.assertContains(response, "parálisis cerebral")
        self.assertContains(response, "nueve naciones")
        self.assertContains(response, "Miracles Now Heavenly Vision")
        self.assertContains(response, "Cojo, Pero No Loco")
        self.assertContains(response, 'datetime="2026-10-12"')
        self.assertContains(response, "Lucas 1:37")
        self.assertContains(response, 'class="about-editorial-lead"')
        self.assertContains(response, 'class="about-editorial-spread"')
        self.assertContains(response, 'class="about-editorial-service"')
        self.assertContains(response, "Una promesa más grande")
        for image_name in (
            "pastor-richie-ramos-hero.jpeg",
            "pastor-richie-ramos-closeup.jpeg",
            "pastor-richie-ramos-testimony.jpeg",
            "pastor-richie-ramos-formal.jpeg",
        ):
            with self.subTest(image_name=image_name):
                self.assertContains(response, image_name)

    def test_about_page_contains_church_identity_and_global_vision(self):
        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sobre Nosotros")
        self.assertContains(response, "relación personal con Jesucristo")
        self.assertContains(response, "todas las edades y procedencias")
        self.assertContains(response, "Newark (Nueva Jersey)")
        self.assertContains(response, "Barranquilla (Colombia)")
        self.assertContains(response, "República Dominicana")
        self.assertContains(
            response,
            "Amar a Dios. Amar a las Personas.",
        )

    def test_about_page_contains_beliefs_and_core_values(self):
        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="aboutBeliefsTitle"')
        self.assertContains(response, "Creencias.")
        self.assertContains(response, "Palabra de Dios inspirada")
        self.assertContains(response, "Padre, Hijo y Espíritu Santo")
        self.assertContains(response, "salvación es por la gracia de Dios")
        self.assertContains(response, "matrimonio bíblico")
        self.assertContains(response, 'id="aboutValuesTitle"')
        self.assertContains(response, "Fundamentales.")
        for value in (
            "Cristo Primero",
            "Verdad Bíblica",
            "Oración",
            "Amor",
            "Integridad",
            "Compasión",
            "Avivamiento",
            "Discipulado",
            "Evangelismo",
            "Excelencia",
        ):
            with self.subTest(value=value):
                self.assertContains(response, value)

    def test_about_navigation_tab_is_available_and_active(self):
        about_response = self.client.get(reverse("about"))
        home_response = self.client.get(reverse("home"))

        self.assertContains(
            about_response,
            '<a class="nav-link active" href="/nosotros/">Nosotros</a>',
            html=True,
        )
        self.assertContains(
            home_response,
            '<a class="nav-link" href="/nosotros/">Nosotros</a>',
            html=True,
        )


class LanguageSelectionTests(TestCase):
    def select_language(self, language, next_url="/"):
        return self.client.post(
            reverse("set_language"),
            {"language": language, "next": next_url},
        )

    def test_menu_selection_activates_language_and_sets_cookie(self):
        expectations = (
            ("es", "Nosotros", "Solicita Tu"),
            ("en", "About Us", "Request Your"),
            ("pt", "Sobre Nós", "Peça a Sua"),
        )

        for code, navigation, bible_heading in expectations:
            with self.subTest(language=code):
                response = self.client.post(
                    reverse("set_language"),
                    {"language": code, "next": reverse("home")},
                    follow=True,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["Content-Language"], code)
                self.assertEqual(
                    self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value,
                    code,
                )
                self.assertContains(response, f'<html lang="{code}">')
                self.assertContains(response, navigation)
                self.assertContains(response, bible_heading)
                self.assertContains(response, 'class="language-switcher"')

    def test_language_menu_keeps_current_path_without_domain_links(self):
        response = self.client.get(f'{reverse("home")}?campaign=summer')

        self.assertContains(
            response,
            f'action="{reverse("set_language")}"',
            count=3,
        )
        self.assertContains(
            response,
            'name="next" value="/?campaign=summer"',
            count=3,
        )
        self.assertNotContains(response, "en.iglesia.test")
        self.assertNotContains(response, "pt.iglesia.test")
        self.assertNotContains(response, 'hreflang="x-default"')

    def test_dynamic_banner_uses_the_selected_language(self):
        banner = Banner.objects.create(
            title="Aviso base",
            description="<p>Contenido base</p>",
            is_active=True,
        )
        Banner.objects.filter(pk=banner.pk).update(
            title_es="Bienvenidos",
            description_es="<p>Mensaje en español</p>",
            title_en="Welcome",
            description_en="<p>English message</p>",
            title_pt="Bem-vindos",
            description_pt="<p>Mensagem em português</p>",
        )

        for language, expected in (
            ("es", "Bienvenidos"),
            ("en", "Welcome"),
            ("pt", "Bem-vindos"),
        ):
            with self.subTest(language=language):
                self.select_language(language)
                response = self.client.get(reverse("home"))
                self.assertContains(response, expected)
