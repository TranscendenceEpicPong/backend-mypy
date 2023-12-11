from django.http import JsonResponse, HttpResponse
from .service import checkAccessToken

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path in ['/authentification/login', '/authentification/register']:
            return response

        if 'Authorization' not in request.headers:
            return HttpResponse("Unauthorized", status=401)

        access_token = request.headers['Authorization'].replace("Bearer ", "", 1)

        if not checkAccessToken(access_token):
            return HttpResponse("Unauthorized", status=401)

        return response
