from django.contrib.auth.middleware import AuthenticationMiddleware
import jwt
import json


class CustomAuthenticationMiddleware(AuthenticationMiddleware):
    def _unAuthorized(self, request):
        response = self.get_response(request)
        response.status_code = 401
        response.content = json.dumps({
            "message": "Accès refusé"
        })
        return response

    def process_request(self, request):
        if request.path in ['/authentication/login', '/authentication/register']:
            return None

        authorization = request.COOKIES.get('authorization')
        sessionId = request.COOKIES.get('sessionid')
        session_key = request.session.session_key

        try:
            token = jwt.decode(authorization, 'ENV_secret', algorithms=['HS256'])
        except:
            return self._unAuthorized(request)

        if token.get('sessionId') != session_key:
            return self._unAuthorized(request)
