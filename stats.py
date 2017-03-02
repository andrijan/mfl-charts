import json

from collections import Counter
from datetime import date, datetime

from flask import Flask, render_template

from mfl.api import Api


app = Flask(__name__)


@app.route('/')
def stats():
    instance = Api(2017)
    all_players = instance.players(details=True)['players']['player']
    rosters = instance.rosters(76173)['rosters']['franchise']
    league = instance.league(76173)['league']['franchises']['franchise']
    roster_players = {}
    for roster in rosters:
        r = next((item for item in league if item['id'] == roster['id']))
        roster_players[r['name']] = roster['player']
    today = date.today()
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            p = next(
                (item for item in all_players if item['id'] == player['id'])
            )
            try:
                born = datetime.fromtimestamp(float(p['birthdate']))
            except KeyError:
                continue
            age = (
                today.year -
                born.year -
                ((today.month, today.day) < (born.month, born.day))
            )
            player_stats.append(age)
        age_distribution = Counter(player_stats).most_common()
        for i in range(20):
            if i + 20 not in dict(age_distribution):
                age_distribution.append((i + 20, 0))
        age_distribution = sorted(age_distribution)
        franchises.append((franchise, age_distribution))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="playerAge"
    )


@app.route('/colleges')
def colleges():
    instance = Api(2017)
    all_players = instance.players(details=True)['players']['player']
    rosters = instance.rosters(76173)['rosters']['franchise']
    league = instance.league(76173)['league']['franchises']['franchise']
    roster_players = {}
    for roster in rosters:
        r = next((item for item in league if item['id'] == roster['id']))
        roster_players[r['name']] = roster['player']
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            p = next(
                (item for item in all_players if item['id'] == player['id'])
            )
            try:
                college = p['college']
            except KeyError:
                continue
            player_stats.append(college)
        college_distribution = Counter(player_stats).most_common()
        college_distribution = sorted(college_distribution)
        franchises.append((franchise, json.dumps(college_distribution)))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="playerColleges"
    )


@app.route('/weight_height')
def weight_height():
    instance = Api(2017)
    all_players = instance.players(details=True)['players']['player']
    rosters = instance.rosters(76173)['rosters']['franchise']
    league = instance.league(76173)['league']['franchises']['franchise']
    roster_players = {}
    for roster in rosters:
        r = next((item for item in league if item['id'] == roster['id']))
        roster_players[r['name']] = roster['player']
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            p = next(
                (item for item in all_players if item['id'] == player['id'])
            )
            try:
                weight = int(p['weight']) * 0.453592
                height = int(p['height']) * 2.54
            except KeyError:
                continue
            player_stats.append({'x': weight, 'y': height, 'r': 5})
        franchises.append((franchise, json.dumps(player_stats)))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="playerWeightHeight"
    )


@app.route('/draft_round')
def draft_round():
    instance = Api(2017)
    all_players = instance.players(details=True)['players']['player']
    rosters = instance.rosters(76173)['rosters']['franchise']
    league = instance.league(76173)['league']['franchises']['franchise']
    roster_players = {}
    for roster in rosters:
        r = next((item for item in league if item['id'] == roster['id']))
        roster_players[r['name']] = roster['player']
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            p = next(
                (item for item in all_players if item['id'] == player['id'])
            )
            try:
                draft_round = p['draft_round']
            except KeyError:
                draft_round = "FA"
            player_stats.append(draft_round)
        draft_round_distribution = Counter(player_stats).most_common()
        for i in range(6):
            if str(i + 1) not in dict(draft_round_distribution):
                draft_round_distribution.append((str(i + 1), 0))
        if "FA" not in dict(draft_round_distribution):
            draft_round_distribution.append(("FA", 0))
        draft_round_distribution = sorted(draft_round_distribution)
        franchises.append((franchise, json.dumps(draft_round_distribution)))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="draftRound"
    )
