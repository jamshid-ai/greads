from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user


class RegisterationTestCase(TestCase):
    def test_user_account_is_created(self):
        self.client.post(
            reverse("users:register"),
            data={
                "username": "jamshidev",
                "first_name": "Jamshid",
                "last_name": "Mahmudjonov",
                "email": "jmahmudjonov75@gmail.com",
                "password": "somepassword"
            }
        )
        
        user = User.objects.get(username="jamshidev")
        
        self.assertEqual(user.username, "jamshidev")
        self.assertEqual(user.first_name, "Jamshid")
        self.assertEqual(user.last_name, "Mahmudjonov")
        self.assertEqual(user.email, "jmahmudjonov75@gmail.com")
        self.assertNotEqual(user.password, "somepassword")
        self.assertTrue(user.check_password("somepassword"))

    def test_required_fields(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "first_name": "Jamshid",
                "email": "jamshid@gmail.com"
            }
        )
        
        user_count = User.objects.count()
        
        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password", "This field is required.")

    def test_invalid_email(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "jamshidev",
                "first_name": "Jamshid",
                "last_name": "Mahmudjonov",
                "email": "invalid-email",
                "password": "somepassword"
            }
        )
        
        user_count = User.objects.count()
        
        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")
        
    def test_unique_username(self):
        # 1. create a user  
        user = User.objects.create(username="jamshidev", first_name="Jamshid")
        user.set_password("somepass")
        user.save()
        # self.client.post(
        #     reverse("users:register"),
        #     data={
        #         "username": "jamshidev",
        #         "first_name": "Jamshid",
        #         "last_name": "Mahmudjonov",
        #         "email": "jamshid2@gmail.com",
        #         "password": "somepassword"
        #     }
        # )
        
        # 2. try to create another user with that same username
        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "jamshidev",
                "first_name": "Jamshid",
                "last_name": "Mahmudjonov",
                "email": "invalid-email",
                "password": "somepassword"
            }
        )
        
        # 3. check that the second user was not created
        user_count = User.objects.count()
        
        self.assertEqual(user_count, 1)
        
        # 4. check that the form contains the error message
        self.assertFormError(response, "form", "username",
                             "A user with that username already exists.")


class LoginTestCase(TestCase):
    def setUp(self):
        self.db_user = User.objects.create(username="jamshidev", first_name="Jamshid")
        self.db_user.set_password("somepass")
        self.db_user.save()
    
    def test_successful_login(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "jamshidev",
                "password": "somepass"
            }
        )

        user = get_user(self.client)

        self.assertTrue(user.is_authenticated)

    def test_wrong_credential(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "wrong-username",
                "password": "somepass"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.client.post(
            reverse("users:login"),
            data={
                "username": "jamshidev",
                "password": "wrong-passwor"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        
    def test_logout(self):
        self.client.login(username="jamshidev", password="somepass")
        
        self.client.get(reverse("users:logout"))
        
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class ProfileTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("users:profile"))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("users:login") + "?next=/users/profile/")

    def test_profile_detail(self):
        user = User.objects.create(
            username="jamshidev", first_name="Jamshid", last_name="Mahmudjonov", email="jamshid@gmail.com")
        user.set_password("somepass")
        user.save()
        
        self.client.login(username="jamshidev", password="somepass")
        
        response = self.client.get(reverse("users:profile"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.email)

    def test_profile_update(self):
        user = User.objects.create(
            username="jamshidev", first_name="Jamshid", last_name="Mahmudjonov", email="jamshid@gmail.com")
        user.set_password("somepass")
        user.save()
        
        self.client.login(username="jamshidev", password="somepass")

        response = self.client.post(
            reverse("users:profile-edit"),
            data={
                "username": "jamshidev",
                "first_name": "Jamshid",
                "last_name": "Doe",
                "email": "doe@gmail.com"
            }
        )
        user.refresh_from_db()

        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "doe@gmail.com")
        self.assertEqual(response.url, reverse("users:profile"))
