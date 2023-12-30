from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import users.service as users_service
import random
from .models import Token
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
import security.service as security_service
import binascii
import environment.env
import jwt
import datetime

def setNewToken(userId):
    token = random.random()
    user_token = Token(user=User.objects.get(pk=userId), token=token)
    user_token.save()
    return token

def createAccessToken(user):
    ENV_SECRET_KEY = "1234"
    try:
        instance_token = Token.objects.get(user=user['userId'])
        token = instance_token.token
        hash_token = security_service.sha256_hash(f"{token}.{ENV_SECRET_KEY}")
        payload = user.copy()
        payload['token'] = hash_token
        payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        return jwt.encode(payload, ENV_SECRET_KEY, algorithm='HS256')
    except:
        return None

def checkAccessToken(access_token):
    ENV_SECRET_KEY = "1234"

    try:
        payload = jwt.decode(access_token, ENV_SECRET_KEY, algorithms=['HS256'])

        if 'token' not in payload:
            return False

        userId = payload['userId']
        token = payload['token']

        instance_token = Token.objects.get(user=userId)
        hash_token = security_service.sha256_hash(f"{instance_token.token}.{ENV_SECRET_KEY}")

        if token != hash_token:
            return False
    except:
        return False
    
    return True

def login(datas):
    user = users_service.getByEmail(datas.get('email'))

    if user is None:
        return {"datas": None }

    if check_password(datas.get('password'), user.password) == False:
        return {"datas": "Mot de passe incorrect"}

    return createAccessToken({'userId': user.id, 'username': user.username, 'email': user.email})


def register(datas):
    user = None
    try:
        user = users_service.getModel().objects.get(Q(email=datas.get('email')) | Q(username=datas.get('username')))
    except:
        user = None

    if user is not None:
        return {"datas": "Email ou username déjà utilisé"}

    user = users_service.create({
        "username": datas.get('username'),
        "email": datas.get('email'),
        "password": datas.get('password'),
        "confirm_password": datas.get('confirm_password'),
    })

    if ('status' in user) == False:
        return { "datas": user }

    setNewToken(user['userId'])

    return createAccessToken({'userId': user['userId'], 'username': user['username'], 'email': user['email']})
