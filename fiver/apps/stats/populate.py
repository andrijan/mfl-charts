from stats import Api

from . import models


def populate_results(league_id, year):
    instance = Api(year)
    weekly_results = instance.weekly_results(
        league_id, "YTD"
    )['allWeeklyResults']['weeklyResults']

    for week in weekly_results:
        try:
            matchups = week['matchup']
        except KeyError:
            continue
        for matchup in matchups:
            for franchise in matchup['franchise']:
                f = models.Franchise.objects.get(franchise_id=franchise['id'])
                result = models.Result.objects.create(
                    franchise=f,
                    week=week['week'],
                    year=year,
                    result=franchise['result'],
                )
                for player in franchise['player']:
                    try:
                        p = models.Player.objects.get(player_id=player['id'])
                    except models.Player.DoesNotExist:
                        continue
                    models.PlayerResult.objects.create(
                        result=result,
                        player=p,
                        started=player['status'] == 'starter',
                        should_have_started=player['shouldStart'] == '1',
                        points=player['score'] or 0.0,
                    )
