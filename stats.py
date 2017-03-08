import json

from collections import Counter
from datetime import date, datetime

from flask import Flask, render_template

from mfl.api import Api


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("base.html")


@app.route('/team/<franchise_id>')
def team(franchise_id):
    players = get_players(franchise_id=franchise_id)[franchise_id]
    players = sorted(players, key=lambda k: k['average_points'], reverse=True)
    return render_template(
        "team.html",
        players=players,
    )


def get_players(position=None, franchise_id=None):
    """
    Returns a dictionary where the keys are the names of the franchises and
    the values are the players with the data
    """
    inst = Api(2017)
    all_players = inst.players(details=True)['players']['player']
    rosters = inst.rosters(76173, franchise_id)['rosters']['franchise']
    league = inst.league(76173)['league']['franchises']['franchise']
    inst = Api(2016)
    average_scores = inst.player_scores(
        76173,
        week='AVG',
    )['playerScores']['playerScore']
    total_scores = inst.player_scores(
        76173,
        week='YTD',
    )['playerScores']['playerScore']
    roster_players = {}
    if franchise_id:
        rosters = [rosters]
    today = date.today()
    for roster in rosters:
        r = next((item for item in league if item['id'] == roster['id']))
        players = []
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
            if position:
                if p['position'] != position:
                    continue
            name = p['name'].split(',')
            p['name'] = name[1].strip() + " " + name[0]
            players.append(p)
        roster_players[r['id']] = players
    return roster_players


@app.route('/age')
@app.route('/age/<position>')
def age(position=None):
    roster_players = get_players(position)
    today = date.today()
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            try:
                born = datetime.fromtimestamp(float(player['birthdate']))
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
    title = "Age distribution"
    if position:
        title += " {}".format(position)
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="playerAge",
        title=title,
    )


@app.route('/colleges')
@app.route('/colleges/<position>')
def colleges(position=None):
    roster_players = get_players(position)
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            try:
                college = player['college']
            except KeyError:
                continue
            player_stats.append(college)
        college_distribution = Counter(player_stats).most_common()
        college_distribution = sorted(college_distribution)
        franchises.append((franchise, json.dumps(college_distribution)))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="playerColleges",
        title="College Distribution",
    )


@app.route('/weight_height')
@app.route('/weight_height/<position>')
def weight_height(position=None):
    roster_players = get_players(position)
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            try:
                weight = int(player['weight']) * 0.453592
                height = int(player['height']) * 2.54
            except KeyError:
                continue
            player_stats.append({'x': weight, 'y': height, 'r': 5})
        franchises.append((franchise, json.dumps(player_stats)))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="playerWeightHeight",
        title="Weight and Height Distribution",
    )


@app.route('/draft_round')
@app.route('/draft_round/<position>')
def draft_round(position=None):
    roster_players = get_players(position)
    franchises = []
    for franchise, players in roster_players.items():
        player_stats = []
        for player in players:
            try:
                draft_round = player['draft_round']
            except KeyError:
                draft_round = "Undrafted"
            player_stats.append(draft_round)
        draft_round_distribution = Counter(player_stats).most_common()
        for i in range(7):
            if str(i + 1) not in dict(draft_round_distribution):
                draft_round_distribution.append((str(i + 1), 0))
        if "Undrafted" not in dict(draft_round_distribution):
            draft_round_distribution.append(("Undrafted", 0))
        draft_round_distribution = sorted(draft_round_distribution)
        franchises.append((franchise, json.dumps(draft_round_distribution)))
    return render_template(
        "stats.html",
        franchises=franchises,
        graph_class="draftRound",
        title="Draft Round Distribution",
    )
