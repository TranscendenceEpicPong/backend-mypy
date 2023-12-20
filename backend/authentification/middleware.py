from django.http import JsonResponse, HttpResponse
from .service import checkAccessToken


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path in ['/authentification/login', '/authentification/register']:
            return response
        if 'Cookie' not in request.headers:
            return HttpResponse("Unauthorized", status=401)
        if 'authorization' not in request.headers['Cookie']:
            return HttpResponse("Unauthorized", status=401)
        cookies = request.headers['Cookie'].split(';')

        for cookie in cookies:
            parts = cookie.split('=')
            if parts[0] == 'authorization':
                if checkAccessToken(parts[1]) == False:
                    return HttpResponse("Unauthorized", status=401)
                else:
                    return response
        return HttpResponse("Unauthorized", status=401)
