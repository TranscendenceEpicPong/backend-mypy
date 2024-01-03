from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    request.session['initialized'] = True
    return HttpResponse('Session initialisée')