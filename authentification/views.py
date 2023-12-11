from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from users.service import create as create_user, login as login_user
import random
from .models import Token
from django.contrib.auth.models import User
from security.service import sha256_hash
import binascii
import authentification.service as service

@require_POST
def login(request):
    user = service.login({
        "email": request.POST.get('email'),
        "password": request.POST.get('password'),
    })

    return JsonResponse({
        "datas": user
    })

@require_POST
def register(request):
    user = service.register({
        "username": request.POST.get('username'),
        "email": request.POST.get('email'),
        "password": request.POST.get('password'),
        "confirm_password": request.POST.get('confirm_password'),
    })

    print(user)
    return JsonResponse(user)