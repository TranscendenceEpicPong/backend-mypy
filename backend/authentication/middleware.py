import jwt
from django.http import HttpResponse


def CustomAuthenticationMiddleware(get_response):
    def middleware(request):
        if request.path in ['/authentication/login', '/authentication/register']:
            return get_response(request)

        authorization = request.COOKIES.get('authorization')
        sessionId = request.COOKIES.get('sessionid')
        session_key = request.session.session_key

        try:
            token = jwt.decode(authorization, 'ENV_secret', algorithms=['HS256'])
        except:
            return HttpResponse("Wrong token", status=401)

        if token.get('sessionId') != session_key:
            return HttpResponse("Wrong token", status=401)

        response = get_response(request)

        return response

    return middleware
