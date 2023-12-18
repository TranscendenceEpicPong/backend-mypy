from tournament_app.models import Tournament, Match, RegistrationTournament, TournamentRanking

def update_tournament_results(tournament):

	matches = Match.objects.filter(tournament=tournament)
	for match in matches:
		winner = match.get_winner()
		loser = match.get_loser()

		registration_winner = RegistrationTournament.objects.get(user=winner, tournament=tournament)
		registration_winner.points += 3
		registration_loser = RegistrationTournament.objects.get(user=loser, tournament=tournament)

		if match.score_player1 > match.score_player2:
			registration_winner.goal_average += match.score_player1 - match.score_player2
			registration_winner.goal_conceded += match.score_player2
			registration_loser.goal_average += match.score_player2 - match.score_player1
			registration_loser.goal_conceded += match.score_player1
		else:
			registration_winner.goal_average += match.score_player2 - match.score_player1
			registration_winner.goal_conceded += match.score_player1
			registration_loser.goal_average += match.score_player1 - match.score_player2
			registration_loser.goal_conceded += match.score_player2
		
		registration_winner.save()
		registration_loser.save()

		registration_loser.goal_average += match.score_player2 - match.score_player1
		registration_loser.goal_conceded += match.score_player1

	TournamentRanking.update_ranking(tournament)

def reset_ranking(tournament):
	participants = RegistrationTournament.objects.filter(tournament=tournament)

	for participant in participants:
		participant.points = 0
		participant.goal_average = 0
		participant.goal_conceded = 0
		participant.save()

