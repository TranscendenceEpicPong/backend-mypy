import unittest
import random
import string

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.test import TestCase, Client
from django.test.utils import override_settings, modify_settings
from django.urls import path, include
from django.conf import settings

from authentification import views


@login_required
def restricted_view(request):
    return HttpResponse("Hello World")


def unrestricted_view(request):
    return HttpResponse("Hello World")


def user_details_view(request: HttpRequest):
    if request.user.is_authenticated:
        return HttpResponse(request.user.email)
    else:
        return HttpResponse("anonymous")


random_path = ''.join(random.choices(string.ascii_lowercase, k=5))

urlpatterns = [
    path(random_path, views.login),
    path("authentification/login", views.login),
    path("default_auth/", include("django.contrib.auth.urls")),
    path("restricted", restricted_view),
    path("unrestricted", unrestricted_view),
    path("user_details", user_details_view),
]


class AuthClient(Client):
    def call_unrestricted(self):
        return self.get('/unrestricted')

    def call_restricted(self):
        return self.get('/restricted')

    def call_user_details(self):
        return self.get('/user_details')


@override_settings(ROOT_URLCONF=__name__)
class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.creds = {
            "username": "john",
            "email": "lennon@thebeatles.com",
            "password": "johnpassword"
        }
        User.objects.create_user(**self.creds)

    @modify_settings(MIDDLEWARE={
        'remove': 'authentification.middleware.AuthenticationMiddleware',
    })
    def test_default_authentication_system(self):
        client = AuthClient()
        auth_response = client.post('/default_auth/login/', {
            "username": self.creds["username"],
            "password": self.creds["password"],
        })

        response = client.call_restricted()
        self.assertEqual(response.status_code, 200)

        response = client.call_unrestricted()
        self.assertEqual(response.status_code, 200)

        response = client.call_user_details()
        self.assertEqual(response.content.decode(), self.creds["email"])

    def test_login_endpoint_should_not_be_static(self):
        client = AuthClient()
        auth_response = client.post(f"/{random_path}/", {
            "email": self.creds["email"],
            "password": self.creds["password"],
        })
        self.assertEqual(auth_response.status_code, 200)

    def call_and_assert_unauthenticated(self):
        client = AuthClient()

        response = client.call_unrestricted()
        self.assertEqual(response.status_code, 200)

        response = client.call_user_details()
        self.assertEqual(response.content.decode(), "anonymous")

        return client

    @modify_settings(MIDDLEWARE={
        'remove': 'authentification.middleware.AuthenticationMiddleware',
    })
    @override_settings(LOGIN_URL="/default_auth/login/")
    def test_default_unauthenticated(self):
        client = self.call_and_assert_unauthenticated()

        # By default, Django redirects to the login page
        response = client.call_restricted()
        self.assertRedirects(response, settings.LOGIN_URL + '?next=/restricted', fetch_redirect_response=False)

    def test_custom_unauthenticated(self):
        client = self.call_and_assert_unauthenticated()

        # instead of the default behaviour (redirect), we should just throw 401
        response = client.call_restricted()
        self.assertEqual(response.status_code, 401)


@override_settings(ROOT_URLCONF=__name__)
class CustomAuthenticationTestCase(TestCase):
    def setUp(self):
        self.creds = {
            "username": "john",
            "email": "lennon@thebeatles.com",
            "password": "johnpassword"
        }
        User.objects.create_user(**self.creds)

        self.client = AuthClient()
        auth_response = self.client.post('/authentification/login', {
            "email": self.creds["email"],
            "password": self.creds["password"],
        })
        # this is not a real assertion, just to crash early and have
        # a line to put a breakpoint on if it fails
        assert auth_response.status_code == 200

    def test_call_unrestricted(self):
        response = self.client.call_unrestricted()
        self.assertEqual(response.status_code, 200)

    def test_call_restricted(self):
        response = self.client.call_restricted()
        self.assertEqual(response.status_code, 200)

    def test_call_user_details(self):
        response = self.client.call_user_details()
        self.assertEqual(response.content.decode(), self.creds["email"])
