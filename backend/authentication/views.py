from django.http import HttpResponse
from django.views.decorators.http import require_POST
from users.models import CustomUser as User
import datetime
from django.contrib.auth import authenticate as django_authenticate, login as django_login
from users.form import UserRegisterForm, UserLoginForm
import jwt
from django.db.models import Q

@require_POST
def login(request):
    session_key = request.session.session_key
    username = request.POST.get('username')
    form = UserLoginForm({
        "username": username,
        "password": request.POST.get('password'),
    })
    if form.is_valid() == False:
        return HttpResponse(user.errors)
    user = None
    try:
        user = User.objects.get(Q(username=username) | Q(email=username))
        if user.check_password(form.cleaned_data['password']) == False:
            return HttpResponse("Mot de passe incorrect", 401)
    except User.DoesNotExist:
        return HttpResponse("Identifiant incorrect", 401)

    authentication = django_authenticate(request,
                 username=form.cleaned_data['username'],
                 password=form.cleaned_data['password'])
    django_login(request, authentication)

    token = jwt.encode({
        'username': user.username,
        'email': user.email,
        'sessionId': session_key,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, 'ENV_secret', algorithm='HS256')

    response = HttpResponse("Login successfully!")
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        httponly=True)
    return response

@require_POST
def register(request):
    session_key = request.session.session_key
    if session_key is None:
        request.session['initialized'] = True
        session_key = request.session.session_key

    try:
        user = User.objects.get(
            Q(username=request.POST.get('username')) |
            Q(email=request.POST.get('email'))
        )
        return HttpResponse("User already exists")
    except User.DoesNotExist:
        pass
    user = UserRegisterForm({
        "username": request.POST.get('username'),
        "email": request.POST.get('email'),
        "password": request.POST.get('password'),
        "confirm_password": request.POST.get('confirm_password'),
    })

    if user.is_valid() == False:
        return HttpResponse(user.errors)

    user.save()

    authentication = django_authenticate(request,
                 username=user.cleaned_data['username'],
                 password=user.cleaned_data['password'])
    django_login(request, authentication)

    token = jwt.encode({
        'username': authentication.username,
        'email': authentication.email,
        'sessionId': session_key,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, 'ENV_secret', algorithm='HS256')

    response = HttpResponse("Registration successfully!")
    response.set_cookie('authorization',
                        value=token,
                        path='/',
                        httponly=True)
    return response