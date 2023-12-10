from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import users.service as users_service
import random
from .models import Token
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import security.service as security_service
import binascii
import environment.env


def setNewToken(userId):
    token = random.random()
    user_token = Token(user=User.objects.get(pk=userId), token=token)
    user_token.save()
    return token

def createAccessToken(userId):
    ENV_SECRET_KEY = "1234"

    try:
        instance_token = Token.objects.get(user=userId)
        token = instance_token.token

        hash_token = security_service.sha256_hash(f"{token}.{ENV_SECRET_KEY}")
        payload = {
            "userId": userId,
            "token": hash_token
        }
        payload = security_service.encode_to_hex(json.dumps(payload))
        signature = security_service.sha256_hash(f"{payload}.{ENV_SECRET_KEY}")

        return f"{payload}.{signature}"
    except:
        return None

def checkAccessToken(access_token):
    ENV_SECRET_KEY = "1234"

    parts = access_token.split('.')

    if len(parts) != 2:
        return False
    
    try:
        payload_hexa = parts[0]
        signature = parts[1]

        payload = security_service.decode_from_hex(payload_hexa)
        payload = json.loads(payload)

        if 'userId' not in payload or 'token' not in payload:
            return False

        userId = payload['userId']
        token = payload['token']

        instance_token = Token.objects.get(user=userId)
        hash_token = security_service.sha256_hash(f"{instance_token.token}.{ENV_SECRET_KEY}")

        if token != hash_token or signature != security_service.sha256_hash(f"{payload_hexa}.{ENV_SECRET_KEY}"):
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

    return {"datas": {"access_token": createAccessToken(user.id)}}

def register(datas):
    user = users_service.create({
        "username": datas.get('username'),
        "email": datas.get('email'),
        "password": datas.get('password'),
        "confirm_password": datas.get('confirm_password'),
    })

    if ('status' in user) == False:
        return { "datas": user }

    setNewToken(user['userId'])

    return {
        "datas": {
            "access_token": createAccessToken(user['userId']),
        }
    }
