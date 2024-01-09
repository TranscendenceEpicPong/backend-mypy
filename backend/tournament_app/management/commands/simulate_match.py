#########################################################################################
#                                                                                       #
#   Use :                                                                               #
#          python manage.py simulate_match <tournament_name> <phase>                    #
#                                                                                       #
#   phase option:                                                                       #
#          pool; eighth; quarter; semi; final                                           #
#                                                                                       #
#########################################################################################

from django.core.management.base import BaseCommand
from tournament_app.models import Match, Tournament
import random
from tournament_app.utils import reset_ranking, update_tournament_results


class Command(BaseCommand):
    help = 'Simulate matches with random scores in a given phase'

    def add_arguments(self, parser):
        parser.add_argument('tournament_name', type=str, help='Name of the tournament')
        parser.add_argument('phase', type=str, help='Phase of the tournament')

    def handle(self, *args, **options):
        tournament_name = options['tournament_name']
        phase = options['phase']

        try:
            tournament = Tournament.objects.get(name=tournament_name)
        except Tournament.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tournament "{tournament_name}" does not exist.'))
            return

        if phase not in [choice[0] for choice in Tournament.PHASE_CHOICES]:
            self.stdout.write(self.style.ERROR(f'Invalid phase: {phase}.'))
            return

        matches = Match.objects.filter(tournament=tournament, round_name=f'{phase.capitalize()} Match')

        if not matches:
            self.stdout.write(self.style.ERROR(f'No matches found for phase "{phase}" in tournament "{tournament_name}".'))
            return

        self.stdout.write(self.style.SUCCESS(f'Simulating matches for phase "{phase}" in tournament "{tournament_name}"...'))

        for match in matches:
            winner = random.choice([match.player1, match.player2])
            loser = match.player2 if winner == match.player1 else match.player1

            match.score_player1 = 3 if winner == match.player1 else random.randint(0, 2)
            match.score_player2 = 3 if winner == match.player2 else random.randint(0, 2)

            match.save()

            self.stdout.write(self.style.SUCCESS(f'Match: {match.player1.username} vs {match.player2.username} - Scores: {match.score_player1}-{match.score_player2}'))

        tournament = Tournament.objects.get(name=tournament_name)
        if phase == 'pool':
            update_tournament_results(tournament)
            self.stdout.write(self.style.SUCCESS(f'Ranking in tournament "{tournament_name}" is uptade.'))


        self.stdout.write(self.style.SUCCESS('Simulation complete.'))