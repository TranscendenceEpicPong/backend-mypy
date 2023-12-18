from tournament_app.models import Tournament, Match, RegistrationTournament, TournamentRanking

def update_tournament_results(tournament):

    matches = Match.objects.filter(tournament=tournament, round_name='Pool Match')
    for match in matches:
        winner_user = match.get_winner()
        loser_user = match.get_loser()

        winner = RegistrationTournament.objects.get(user=winner_user, tournament=tournament)
        winner.points += 3
        loser = RegistrationTournament.objects.get(user=loser_user, tournament=tournament)

        #####################################################
        #                                                   #
        #  goal_average = goal scored - goal conceded       #
        #                                                   #
        #  e.g. :         player1 vs player2                #
        #                       3-2                         #
        #  player1 : goal_average = 1 ; goal_conceded = 2   #
        #  player2 : goal_average = -1 ; goal_conceded = 3  #
        #                                                   #
        #####################################################

        # if player1 won
        if match.score_player1 > match.score_player2:
            winner.goal_average += match.score_player1 - match.score_player2
            winner.goal_conceded += match.score_player2
            loser.goal_average += match.score_player2 - match.score_player1
            loser.goal_conceded += match.score_player1
        # if player2 won
        else:
            winner.goal_average += match.score_player2 - match.score_player1
            winner.goal_conceded += match.score_player1
            loser.goal_average += match.score_player1 - match.score_player2
            loser.goal_conceded += match.score_player2
        
        winner_user.save()
        loser_user.save()

        loser.goal_average += match.score_player2 - match.score_player1
        loser.goal_conceded += match.score_player1

    TournamentRanking.update_ranking(tournament)

def reset_ranking(tournament):
    participants = RegistrationTournament.objects.filter(tournament=tournament)

    for participant in participants:
        participant.points = 0
        participant.goal_average = 0
        participant.goal_conceded = 0
        participant.save()

