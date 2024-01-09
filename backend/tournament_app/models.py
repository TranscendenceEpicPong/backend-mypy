from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
import random
from itertools import zip_longest
import logging # error

# Create your models here.

class Tournament(models.Model):
    name = models.CharField(max_length=50)
    creator_alias = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tournament')
    participants = models.ManyToManyField(User, through='RegistrationTournament')
    is_open = models.BooleanField(default=True)
    max_participants = models.PositiveIntegerField(default=20)
    ranking = models.ManyToManyField('RegistrationTournament', through='TournamentRanking', related_name='tournament_ranking')

    PHASE_CHOICES = [
        ('no', 'not begin'),
        ('pool', 'Pool Phase'),
        ('eighth', 'Eighth Phase'),
        ('quarter', 'Quarter Phase'),
        ('semi', 'Semi Phase'),
        ('final', 'Final Phase'),
    ]

    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='no')

    def __str__(self):
        return f"{self.name} (Creator: {self.creator_alias})"
        
    def is_full(self):
        return self.participants.count() == self.max_participants
        
    def start_next_phase(self):
        if self.participants.count() <= 3 and self.participants.count() > 20:
            logging.error(f'Tournament "{self.name}" invalid number of participants.')
            return 
        if self.phase == 'no':
            self.is_open = False
            self.phase = 'pool'
            self.save()
            self.organize_pool_matches()
        elif self.phase == 'pool' and self.participants.count() >= 16:
            self.phase = 'eighth'
            self.save()
            self.organize_eighth_matches()
        elif (self.phase == 'pool' and self.participants.count() >= 8) or self.phase == 'eighth':
            self.phase = 'quarter'
            self.save()
            self.organize_quarter_matches()
        elif (self.phase == 'pool' and self.participants.count() >= 4) or self.phase == 'quarter':
            self.phase = 'semi'
            self.save()
            self.organize_semi_matches()
        elif (self.phase == 'pool' and self.participants.count() >= 2) or self.phase == 'semi':
            self.phase = 'final'
            self.save()
            self.organize_final_match()

    def organize_pool_matches(self):
        participants_list_2free = list(self.participants.all())
        random.shuffle(participants_list_2free)
        participants_list_1free = []
        i = 0
        while participants_list_2free or participants_list_1free :
            if participants_list_2free:
                player1 = random.choice(participants_list_2free)
                participants_list_2free.remove(player1)

                if participants_list_2free:
                    opponent1 = random.choice(participants_list_2free)
                    participants_list_2free.remove(opponent1)
                    participants_list_1free.append(opponent1)
                else:
                    opponent1 = random.choice(participants_list_1free)
                    participants_list_1free.remove(opponent1)

                if participants_list_2free:
                    opponent2 = random.choice(participants_list_2free)
                    participants_list_2free.remove(opponent2)
                    participants_list_1free.append(opponent2)
                else:
                    opponent2 = random.choice(participants_list_1free)
                    participants_list_1free.remove(opponent2)

                match1 = Match.objects.create(
                    tournament=self,
                    player1=player1,
                    player2=opponent1,
                    round_name='Pool Match',
                )
                match2 = Match.objects.create(
                    tournament=self,
                    player1=player1,
                    player2=opponent2,
                    round_name='Pool Match',
                )
            else:
                player1 = random.choice(participants_list_1free)
                participants_list_1free.remove(player1)

                opponent1 = random.choice(participants_list_1free)
                participants_list_1free.remove(opponent1)

                match = Match.objects.create(
                    tournament=self,
                    player1=player1,
                    player2=opponent1,
                    round_name='Pool Match',
                )

    def organize_eighth_matches(self):
        participants = TournamentRanking.objects.filter(tournament=self).order_by('rank')[:16]
        pairs = list(zip_longest(participants[:8], reversed(participants[8:])))

        for i, pair in enumerate(pairs, start=1):
            match = Match.objects.create(
                tournament=self,
                player1=pair[0].registration.user,
                player2=pair[1].registration.user,
                round_name='Eighth Match',
            )
        self.save()

    def organize_quarter_matches(self):
        if self.participants.count() < 16:
            participants = TournamentRanking.objects.filter(tournament=self).order_by('rank')[:8]
        else:
            winners_eighth = [match.get_winner() for match in Match.objects.filter(tournament=self, round_name='Eighth Match')]
            participants = TournamentRanking.objects.filter(registration__user__in=winners_eighth).order_by('rank')

        pairs = list(zip_longest(participants[:4], reversed(participants[4:])))

        for i, pair in enumerate(pairs, start=1):
            match = Match.objects.create(
                tournament=self,
                player1=pair[0].registration.user,
                player2=pair[1].registration.user,
                round_name='Quarter Match',
            )
        self.save()

    def organize_semi_matches(self):
        if self.participants.count() < 8:
            participants = TournamentRanking.objects.filter(tournament=self).order_by('rank')[:4]
        else:
            winners_quarter = [match.get_winner() for match in Match.objects.filter(tournament=self, round_name='Quarter Match')]
            participants = TournamentRanking.objects.filter(registration__user__in=winners_quarter).order_by('rank')

        pairs = list(zip_longest(participants[:2], reversed(participants[2:])))
        
        for i, pair in enumerate(pairs, start=1):
            match = Match.objects.create(
                tournament=self,
                player1=pair[0].registration.user,
                player2=pair[1].registration.user,
                round_name='Semi Match',
            )
        self.save()

    def organize_final_match(self):
        if self.participants.count() < 4:
            participants = TournamentRanking.objects.filter(tournament=self).order_by('rank')[:2]
        else:
            participants = [match.get_winner() for match in Match.objects.filter(tournament=self, round_name='Semi Match')]

        finalists = RegistrationTournament.objects.filter(user__in=participants)

        final_match = Match.objects.create(
            tournament=self,
            player1=finalists[0].user,
            player2=finalists[1].user,
            round_name='Final Match',
        )
        self.save()

    def calculate_ranking(self):
        participants = RegistrationTournament.objects.filter(tournament=self).order_by('-points', '-goal_average', 'goal_conceded', '?')
        return participants
        
    def get_ranking(self):
        return TournamentRanking.objects.filter(tournament=self).order_by('rank')



class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1_matches')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2_matches')
    round_name = models.CharField(max_length=50)
    score_player1 = models.PositiveIntegerField(default=0)
    score_player2 = models.PositiveIntegerField(default=0)

    def get_winner(self):
        if self.score_player1 > self.score_player2:
            return self.player1
        else:
            return self.player2
        
    def get_loser(self):
        if self.score_player2 > self.score_player1:
            return self.player1
        else:
            return self.player2


class RegistrationTournament(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50)
    points = models.PositiveIntegerField(default=0)
    goal_average = models.IntegerField(default=0)
    goal_conceded = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ('tournament', 'alias')

class TournamentRanking(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    registration = models.ForeignKey(RegistrationTournament, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()

    class Meta:
        ordering = ['rank']

    def update_ranking(self, tournament):
        participants = RegistrationTournament.objects.filter(tournament=tournament).order_by('-points', '-goal_average', 'goal_conceded', '?')
        for i, participant in enumerate(participants, start=1):
            TournamentRanking.objects.update_or_create(tournament=tournament, registration=participant, defaults={'rank': i})