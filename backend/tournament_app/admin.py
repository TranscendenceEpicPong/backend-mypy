from django.contrib import admin
from .models import Tournament, RegistrationTournament, Match

# Register your models here.

# affichage des participants du tournoi
class RegistrationTournamentInline(admin.TabularInline):
    model = RegistrationTournament
    extra = 1

class MatchInline(admin.TabularInline):
    model = Match
    extra = 0 

class TournamentAdmin(admin.ModelAdmin):
    inlines = [RegistrationTournamentInline, MatchInline]

    actions = ['delete_all_matches']

    @admin.action(description="Supprimer tous les matchs du tournoi")
    def delete_all_matches(self, request, queryset):
        for tournament in queryset:
            tournament.match_set.all().delete()


admin.site.register(Tournament, TournamentAdmin)