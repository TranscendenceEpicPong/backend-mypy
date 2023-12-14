from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import json
from users.service import create as create_user, login as login_user
import random
from .models import Token
from django.contrib.auth.models import User
from security.service import sha256_hash
import binascii
import authentification.service as service
import datetime

def test(request):
    print("TEST")
    return HttpResponse("Test")

@require_POST
def login(request):
    token = service.login({
        "email": request.POST.get('email'),
        "password": request.POST.get('password'),
    })

    response = HttpResponse("Login successfully!")
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        httponly=True)
    return response

@require_POST
def register(request):
    token = service.register({
        "username": request.POST.get('username'),
        "email": request.POST.get('email'),
        "password": request.POST.get('password'),
        "confirm_password": request.POST.get('confirm_password'),
    })

    response = HttpResponse("Registration successfully!")
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        httponly=True)
    return response