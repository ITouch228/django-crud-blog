from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AccountModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="user@test.com", password="pass1234")
        self.assertEqual(user.email, "user@test.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@test.com", password="adminpass1234"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="pass1234")

    def test_str_returns_email(self):
        user = User.objects.create_user(email="hello@test.com", password="pass1234")
        self.assertEqual(str(user), "hello@test.com")

    def test_get_full_name(self):
        user = User.objects.create_user(
            email="name@test.com", password="pass1234",
            first_name="Ivan", last_name="Petrov",
        )
        self.assertEqual(user.get_full_name(), "Ivan Petrov")

    def test_get_short_name(self):
        user = User.objects.create_user(
            email="short@test.com", password="pass1234", first_name="Ivan"
        )
        self.assertEqual(user.get_short_name(), "Ivan")

    def test_get_short_name_fallback_to_email(self):
        user = User.objects.create_user(email="noname@test.com", password="pass1234")
        self.assertEqual(user.get_short_name(), "noname@test.com")


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page(self):
        response = self.client.get("/accounts/register/")
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post("/accounts/register/", {
            "email": "new@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email="dup@test.com", password="pass1234")
        response = self.client.post("/accounts/register/", {
            "email": "dup@test.com",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email="dup@test.com").count(), 1)

    def test_login_page(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        User.objects.create_user(email="login@test.com", password="pass1234")
        response = self.client.post("/accounts/login/", {
            "username": "login@test.com",
            "password": "pass1234",
        })
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        User.objects.create_user(email="login@test.com", password="pass1234")
        response = self.client.post("/accounts/login/", {
            "username": "login@test.com",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        User.objects.create_user(email="out@test.com", password="pass1234")
        self.client.login(email="out@test.com", password="pass1234")
        response = self.client.post("/accounts/logout/")
        self.assertEqual(response.status_code, 302)
