from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tournament_app.models import Tournament, RegistrationTournament

class Command(BaseCommand):
    help = 'Create a new tournament'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the tournament')
        parser.add_argument('max_participants', type=int, help='Maximum number of participants')

    def handle(self, *args, **options):
        name = options['name']
        max_participants = options['max_participants']

        # Créer le premier utilisateur (s'il n'existe pas déjà)
        first_user, created = User.objects.get_or_create(username='user1')
        if created:
            first_user.set_password('')
            first_user.save()

        # Créer le tournoi et ajouter le premier utilisateur comme créateur
        tournament = Tournament.objects.create(
            name=name,
            max_participants=max_participants,
            creator_alias=first_user,
        )

        self.stdout.write(self.style.SUCCESS(f'Tournament "{name}" created successfully.'))

        for i in range(1, max_participants + 1):
            username = f'user{i}'
            alias = f'alias_user{i}'

            # Créer un utilisateur s'il n'existe pas
            user, created = User.objects.get_or_create(username=username)

            # Inscrire l'utilisateur au tournoi avec l'alias
            RegistrationTournament.objects.create(user=user, tournament=tournament, alias=alias)

            self.stdout.write(self.style.SUCCESS(f'User "{username}" registered with alias "{alias}"'))