from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .forms import ProfileUpdateForm, SignUpForm
from .models import CustomUser


class CustomUserModelTest(TestCase):

    def test_str_returns_username(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )
        self.assertEqual(str(user), "testuser")

    def test_clean_rejects_future_date_of_birth(self):
        user = get_user_model()(
            username="testuser",
            email="test@example.com",
            date_of_birth=date.today() + timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            user.clean()

    def test_clean_accepts_past_date_of_birth(self):
        user = get_user_model()(
            username="testuser",
            email="test@example.com",
            date_of_birth=date(2000, 1, 1),
        )
        try:
            user.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError for a valid date_of_birth")

    def test_clean_accepts_null_date_of_birth(self):
        user = get_user_model()(
            username="testuser",
            email="test@example.com",
            date_of_birth=None,
        )
        try:
            user.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError for null date_of_birth")

    def test_email_is_unique(self):
        get_user_model().objects.create_user(
            username="user1",
            email="dup@example.com",
            password="StrongPass1!",
        )
        with self.assertRaises(Exception):
            get_user_model().objects.create_user(
                username="user2",
                email="dup@example.com",
                password="StrongPass1!",
            )


class SignUpFormTest(TestCase):

    def test_valid_form(self):
        form = SignUpForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form = SignUpForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "DifferentPass1!",
        })
        self.assertFalse(form.is_valid())

    def test_blank_username(self):
        form = SignUpForm(data={
            "username": "",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertFalse(form.is_valid())

    def test_blank_email(self):
        form = SignUpForm(data={
            "username": "testuser",
            "email": "",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertFalse(form.is_valid())

    def test_invalid_email(self):
        form = SignUpForm(data={
            "username": "testuser",
            "email": "not-an-email",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertFalse(form.is_valid())

    def test_weak_password(self):
        form = SignUpForm(data={
            "username": "testuser",
            "email": "test@example.com",
            "password1": "weak",
            "password2": "weak",
        })
        self.assertFalse(form.is_valid())

    def test_duplicate_email(self):
        get_user_model().objects.create_user(
            username="existing",
            email="dup@example.com",
            password="StrongPass1!",
        )
        form = SignUpForm(data={
            "username": "newuser",
            "email": "dup@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertFalse(form.is_valid())


class ProfileUpdateFormTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_form_fields(self):
        form = ProfileUpdateForm(instance=self.user)
        expected = {"username", "phone_number", "profile_picture", "bio", "date_of_birth"}
        self.assertEqual(set(form.fields.keys()), expected)

    def test_valid_form(self):
        form = ProfileUpdateForm(
            instance=self.user,
            data={
                "username": "updateduser",
                "phone_number": "+1234567890",
                "bio": "Hello!",
            },
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.bio, "Hello!")


class SignUpViewTest(TestCase):

    def test_page_status_code(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_creates_user(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_redirects_to_home(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertRedirects(response, reverse("pages:home"))

    def test_logs_in_after_signup(self):
        response = self.client.post(reverse("accounts:signup"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        }, follow=True)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_rejects_duplicate_email(self):
        get_user_model().objects.create_user(
            username="existing",
            email="dup@example.com",
            password="StrongPass1!",
        )
        response = self.client.post(reverse("accounts:signup"), {
            "username": "newuser",
            "email": "dup@example.com",
            "password1": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "email",
            "User with this Email address already exists.",
        )


class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('accounts:profile')}",
        )

    def test_authenticated_access(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertTemplateUsed(response, "accounts/profile_update.html")

    def test_profile_update(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {
            "username": "updateduser",
            "bio": "New bio",
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updateduser")
        self.assertEqual(self.user.bio, "New bio")


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_page_status_code(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "username": "test@example.com",
            "password": "StrongPass1!",
        })
        self.assertRedirects(response, reverse("pages:home"))

    def test_login_failure(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct")


class LogoutTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass1!",
        )

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("pages:home"))
