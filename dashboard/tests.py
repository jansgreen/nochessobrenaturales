from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()
PASSWORD = "ClaveSegura-2026!"


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="miembro",
            email="miembro@example.com",
            password=PASSWORD,
        )
        self.staff = User.objects.create_user(
            username="editor",
            email="editor@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        self.superuser = User.objects.create_superuser(
            username="administrador",
            email="admin@example.com",
            password=PASSWORD,
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_member_gets_personal_dashboard_without_management_tools(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bienvenido a tu espacio personal")
        self.assertNotContains(response, "Administrar el sitio")
        self.assertNotContains(response, "Usuarios y accesos")

    def test_staff_gets_all_content_tools_but_not_user_management(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        for label in (
            "Banners",
            "Eventos",
            "Videos",
            "Galería",
            "Filas destacadas",
            "Equipo ministerial",
            "Donaciones",
        ):
            with self.subTest(label=label):
                self.assertContains(response, label)
        self.assertNotContains(response, "Usuarios y accesos")

    def test_superuser_gets_content_and_user_management(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuarios y accesos")
        self.assertContains(response, reverse("dashboard:user_list"))

    def test_staff_cannot_open_user_management(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("dashboard:user_list"))

        self.assertEqual(response.status_code, 403)


class DashboardUserManagementTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="root-admin",
            email="root@example.com",
            password=PASSWORD,
        )
        self.member = User.objects.create_user(
            username="persona",
            email="persona@example.com",
            password=PASSWORD,
        )
        self.client.force_login(self.superuser)

    def test_superuser_can_create_staff_account(self):
        response = self.client.post(
            reverse("dashboard:user_create"),
            {
                "username": "nuevo-editor",
                "first_name": "Nuevo",
                "last_name": "Editor",
                "email": "editor.nuevo@example.com",
                "access_level": "staff",
                "is_active": "on",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:user_list"),
            fetch_redirect_response=False,
        )
        account = User.objects.get(username="nuevo-editor")
        self.assertTrue(account.is_staff)
        self.assertFalse(account.is_superuser)
        self.assertTrue(account.check_password(PASSWORD))

    def test_superuser_can_change_an_accounts_access_level(self):
        response = self.client.post(
            reverse("dashboard:user_update", args=[self.member.pk]),
            {
                "username": self.member.username,
                "first_name": "María",
                "last_name": "Rivera",
                "email": self.member.email,
                "access_level": "staff",
                "is_active": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:user_list"),
            fetch_redirect_response=False,
        )
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_staff)
        self.assertFalse(self.member.is_superuser)

    def test_superuser_can_set_an_accounts_password(self):
        new_password = "OtraClave-Segura-2026!"

        response = self.client.post(
            reverse("dashboard:user_password", args=[self.member.pk]),
            {
                "new_password1": new_password,
                "new_password2": new_password,
            },
        )

        self.assertRedirects(
            response,
            reverse("dashboard:user_list"),
            fetch_redirect_response=False,
        )
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password(new_password))

    def test_superuser_cannot_demote_own_account(self):
        response = self.client.post(
            reverse("dashboard:user_update", args=[self.superuser.pk]),
            {
                "username": self.superuser.username,
                "first_name": "",
                "last_name": "",
                "email": self.superuser.email,
                "access_level": "member",
                "is_active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No puedes reducir tu propio nivel")
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_superuser)

    def test_superuser_cannot_delete_own_account(self):
        response = self.client.post(
            reverse("dashboard:user_delete", args=[self.superuser.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:user_list"),
            fetch_redirect_response=False,
        )
        self.assertTrue(User.objects.filter(pk=self.superuser.pk).exists())

    def test_superuser_can_delete_another_account(self):
        response = self.client.post(
            reverse("dashboard:user_delete", args=[self.member.pk])
        )

        self.assertRedirects(
            response,
            reverse("dashboard:user_list"),
            fetch_redirect_response=False,
        )
        self.assertFalse(User.objects.filter(pk=self.member.pk).exists())
