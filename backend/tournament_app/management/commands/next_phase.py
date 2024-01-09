###########################################################################
#                                                                         #
#   Use :                                                                 #
#          python manage.py next_phase <tournament_name>                  #
#                                                                         #
###########################################################################

from django.core.management.base import BaseCommand
from tournament_app.models import Tournament

class Command(BaseCommand):
    help = 'Start the next phase of a tournament'

    def add_arguments(self, parser):
        parser.add_argument('tournament_name', type=str, help='Name of the tournament')

    def handle(self, *args, **options):
        tournament_name = options['tournament_name']

        try:
            tournament = Tournament.objects.get(name=tournament_name)
            tournament.start_next_phase()
            self.stdout.write(self.style.SUCCESS(f'Successfully started the next phase for tournament "{tournament_name}"'))
        except Tournament.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Tournament "{tournament_name}" does not exist'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred: {str(e)}'))