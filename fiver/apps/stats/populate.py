from bs4 import BeautifulSoup
from datetime import date, datetime
from urllib.request import urlopen

from stats import Api

from . import models


def populate_adp():
    base_url = 'https://www.fantasypros.com/nfl/rankings/'
    ppr = base_url + 'half-point-ppr-cheatsheets.php'
    dynasty = base_url + 'dynasty-overall.php'
    urls = {'adp': ppr, 'dynasty_adp': dynasty}
    for adp_type, url in urls.items():
        page = urlopen(url).read()
        soup = BeautifulSoup(page, 'html5lib')
        table = soup.find('table', {'id': 'data'})
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            try:
                name = " ".join(tds[1].text.strip().split(" ")[:-1])
            except IndexError:
                continue
            try:
                p = models.Player.objects.get(name=name)
            except models.Player.DoesNotExist:
                # Is it Beckham?
                if name == "Odell Beckham Jr.":
                    p = models.Player.objects.get(name="Odell Beckham")
                else:
                    continue

            setattr(p, adp_type, tds[6].text)
            p.save()


def populate_franchises(league_id, year):
    inst = Api(year)
    all_players = inst.players(details=True)['players']['player']
    rosters = inst.rosters(league_id)['rosters']['franchise']
    league = inst.league(league_id)['league']['franchises']['franchise']
    inst = Api(year - 1)
    average_scores = inst.player_scores(
        league_id,
        week='AVG',
    )['playerScores']['playerScore']
    total_scores = inst.player_scores(
        league_id,
        week='YTD',
    )['playerScores']['playerScore']
    today = date.today()
    for roster in rosters:
        r = next((item for item in league if item['id'] == roster['id']))
        f = models.Franchise.objects.create(
            franchise_id=r['id'],
            name=r['name']
        )
        for player in roster['player']:
            p = next(
                (item for item in all_players if item['id'] == player['id'])
            )
            try:
                average = next((
                    item for item in average_scores if (
                        item['id'] == player['id']
                    )
                ))
            except StopIteration:
                average = {'score': 0}
            try:
                total = next((
                    item for item in total_scores if (
                        item['id'] == player['id']
                    )
                ))
            except StopIteration:
                total = {'score': 0}
            try:
                born = datetime.fromtimestamp(float(p['birthdate']))
                age = (
                    today.year -
                    born.year -
                    ((today.month, today.day) < (born.month, born.day))
                )
            except KeyError:
                age = None
            p['age'] = age
            p['average_points'] = float(average['score'])
            p['total_points'] = float(total['score'])
            p['player_id'] = p['id']
            name = p['name'].split(',')
            p['name'] = name[1].strip() + " " + name[0]

            player = models.Player(franchise=f)
            for key, value in p.items():
                try:
                    setattr(player, key, value)
                except:
                    continue
            player.save()


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
