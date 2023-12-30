from .form import UserRegisterForm, UserLoginForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
import json

def create(datas):
    form = UserRegisterForm(datas)
    if form.is_valid():
        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data['password'])
        user.save()
        return {
            'status': 200,
            'userId': user.pk,
            'username': user.username,
            'email': user.email
        }
    return json.loads(form.errors.as_json())

def getModel():
    return User

def getByEmail(email):
    try:
        user = User.objects.get(email=email)
        return user
    except:
        return None


def login(datas):
    form = UserLoginForm(datas)
    if form.is_valid():
        try:
            user = User.objects.get(email=datas.get('email'))

            if (check_password(datas.get('password'), user.password)):
                return {
                    'status': 200,
                    'userId': user.pk,
                    'username': user.username,
                    'email': user.email
                }
            return None
        except User.DoesNotExist:
            return None
    return form.errors.as_json()