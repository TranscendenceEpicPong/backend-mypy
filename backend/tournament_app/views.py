from django.shortcuts import render
from .models import Tournament

# Create your views here.


def tournament(request):
    tournaments = Tournament.objects.all()
    return render(request,
                'tournament.html',
                {'tournaments': tournaments})