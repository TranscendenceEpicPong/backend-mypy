from django.contrib.sessions.middleware import SessionMiddleware

class CustomSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        # if not request.session:
        #     request.session['initialized'] = True
        pass