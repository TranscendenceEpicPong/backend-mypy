from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User

def index(request):
    users = User.objects.all()
    user_list = list(users.values())  # Convertir le queryset en liste de dictionnaires
    return JsonResponse(user_list, safe=False)
