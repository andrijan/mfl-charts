from bs4 import BeautifulSoup
from datetime import date, datetime
from urllib.request import urlopen

from fiver.apps.mfl.api import Api

from . import models


def populate_all_players(year):
    inst = Api(year)
    all_players = inst.players(details=True)['players']['player']
    for player in all_players:
        if player['position'] not in ['RB', 'WR', 'TE', 'QB', 'Def']:
            continue
        p, created = models.Player.objects.get_or_create(
            player_id=player['id']
        )
        for key, value in player.items():
            try:
                setattr(p, key, value)
            except:
                pass
        p.save()


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
        f, _ = models.Franchise.objects.get_or_create(
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

            try:
                player = models.Player.objects.get(player_id=p['player_id'])
            except models.Player.DoesNotExist:
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
        if 'franchise' in week:
            # Bye weeks
            for franchise in week['franchise']:
                result, _ = models.Result.objects.update_or_create(
                    franchise_id=franchise['id'],
                    week=week['week'],
                    year=year,
                    result='BYE',
                    defaults={
                        'points': franchise['score'],
                    }
                )
                for player in franchise['player']:
                    try:
                        p = models.Player.objects.get(player_id=player['id'])
                    except models.Player.DoesNotExist:
                        continue
                    models.PlayerResult.objects.get_or_create(
                        result=result,
                        player=p,
                        started=player['status'] == 'starter',
                        should_have_started=player['shouldStart'] == '1',
                        points=player['score'] or 0.0,
                    )

        for matchup in matchups:
            for franchise in matchup['franchise']:
                if franchise['id'] == matchup['franchise'][0]['id']:
                    opponent_id = matchup['franchise'][1]['id']
                else:
                    opponent_id = matchup['franchise'][0]['id']
                result, _ = models.Result.objects.update_or_create(
                    franchise_id=franchise['id'],
                    week=week['week'],
                    year=year,
                    result=franchise['result'],
                    defaults={
                        'opponent_id': opponent_id,
                        'points': franchise['score'],
                    }
                )
                for player in franchise['player']:
                    try:
                        p = models.Player.objects.get(player_id=player['id'])
                    except models.Player.DoesNotExist:
                        continue
                    models.PlayerResult.objects.get_or_create(
                        result=result,
                        player=p,
                        started=player['status'] == 'starter',
                        should_have_started=player['shouldStart'] == '1',
                        points=player['score'] or 0.0,
                    )


def populate_picks(league_id, year):
    instance = Api(year)
    franchise_picks = instance.future_draft_picks(
        league_id
    )['futureDraftPicks']['franchise']
    for franchise in franchise_picks:
        for pick in franchise['futureDraftPick']:
            models.Pick.objects.create(
                draft_year=pick['year'],
                draft_round=pick['round'],
                franchise_id=pick['originalPickFor'],
                current_franchise_id=franchise['id'],
            )


def populate_trades(league_id, year):
    instance = Api(year)
    trades = instance.transactions(
        league_id, transaction_type="trade"
    )['transactions']['transaction']

    for trade in trades:
        t, created = models.Trade.objects.get_or_create(
            timestamp=trade['timestamp'],
            accepted=True
        )
        if created:
            offer1 = models.TradeOffer.objects.create(
                franchise_id=trade['franchise'],
                trade=t,
                is_initiator=True,
            )
            franchise1_gave_up = trade['franchise1_gave_up'].split(',')[:-1]
            for pick_or_player in franchise1_gave_up:
                if pick_or_player.startswith('FP'):
                    (
                        franchise_id,
                        draft_year,
                        draft_round,
                    ) = pick_or_player.split('_')[1:]
                    pick = models.Pick.objects.get(
                        draft_year=draft_year,
                        draft_round=draft_round,
                        franchise_id=franchise_id
                    )
                    offer1.picks.add(pick)
                else:
                    player = models.Player.objects.get(
                        player_id=pick_or_player
                    )
                    offer1.players.add(player)
            offer1.save()
            offer2 = models.TradeOffer.objects.create(
                franchise_id=trade['franchise2'],
                trade=t,
                is_initiator=False,
            )
            franchise2_gave_up = trade['franchise2_gave_up'].split(',')[:-1]
            for pick_or_player in franchise2_gave_up:
                if pick_or_player.startswith('FP'):
                    (
                        franchise_id,
                        draft_year,
                        draft_round,
                    ) = pick_or_player.split('_')[1:]
                    pick = models.Pick.objects.get(
                        draft_year=draft_year,
                        draft_round=draft_round,
                        franchise_id=franchise_id
                    )
                    offer2.picks.add(pick)
                else:
                    player = models.Player.objects.get(
                        player_id=pick_or_player
                    )
                    offer2.players.add(player)


def populate_auction_draft(league_id, year):
    instance = Api(year)
    draft = instance.auction_results(
        league_id
    )['auctionResults']['auctionUnit']
    for pick in draft['auction']:
        models.PlayerDraft.objects.get_or_create(
            franchise_id=pick['franchise'],
            player_id=pick['player'],
            timestamp=pick['lastBidTime'],
            defaults={
                'bid_amount': pick['winningBid'],
                'draft_year': year,
            }
        )


def populate_waivers(league_id, year):
    instance = Api(year)
    blind_waivers = instance.transactions(
        league_id, transaction_type="bbid_waiver"
    )['transactions']['transaction']
    for waiver in blind_waivers:
        bought_id, amount, sold_id = waiver['transaction'].split('|')
        models.Waiver.objects.get_or_create(
            franchise_id=waiver['franchise'],
            timestamp=waiver['timestamp'],
            player_id=bought_id,
            amount=int(float(amount)),
            adding=True,
            free_agent=False,
        )
        models.Waiver.objects.get_or_create(
            franchise_id=waiver['franchise'],
            timestamp=waiver['timestamp'],
            player_id=sold_id,
            adding=False,
            free_agent=False,
        )
    free_agents = instance.transactions(
        league_id, transaction_type="waiver"
    )['transactions']['transaction']
    for free_agent in free_agents:
        added = free_agent['added'].split(',')
        for player_id in added:
            if player_id:
                models.Waiver.objects.get_or_create(
                    franchise_id=free_agent['franchise'],
                    timestamp=free_agent['timestamp'],
                    player_id=player_id,
                    adding=True,
                    free_agent=True,
                )

        dropped = free_agent['dropped'].split(',')
        for player_id in dropped:
            if player_id:
                models.Waiver.objects.get_or_create(
                    franchise_id=free_agent['franchise'],
                    timestamp=free_agent['timestamp'],
                    player_id=player_id,
                    adding=False,
                    free_agent=True,
                )
