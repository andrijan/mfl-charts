from bs4 import BeautifulSoup
from urllib.request import urlopen

from fiver.apps.mfl.api import Api

from . import models


def populate_league(league_id, year, start_year):
    inst = Api(year)
    league = inst.league(league_id)['league']
    models.League.objects.get_or_create(
        league_id=league['id'],
        defaults={
            'name': league['name'],
            'roster_size': league['rosterSize'],
            'injured_reserve': league['injuredReserve'],
            'taxi_squad': league['taxiSquad'],
            'start_year': start_year,
        }
    )


def populate_all_players(year):
    inst = Api(year)
    all_players = inst.players(details=True)['players']['player']
    for player in all_players:
        if player['position'] not in ['RB', 'WR', 'TE', 'QB', 'Def', 'PK']:
            continue
        p, created = models.Player.objects.get_or_create(
            player_id=player['id']
        )
        player['name'] = " ".join(player['name'].split(", ")[::-1])
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
        rank_type = 'rank' if adp_type == 'adp' else 'dynasty_rank'
        page = urlopen(url).read()
        soup = BeautifulSoup(page, 'html5lib')
        table = soup.find('table', {'id': 'data'})
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            try:
                if tds[2].text.startswith("DST"):
                    name = tds[1].text.strip()
                else:
                    name = " ".join(tds[1].text.strip().split(" ")[:-1])
            except IndexError:
                continue
            try:
                p = models.Player.objects.get(name__iexact=name)
            except models.Player.DoesNotExist:
                # Is it Beckham?
                if name == "Odell Beckham Jr.":
                    p = models.Player.objects.get(name="Odell Beckham")
                elif name == "Robert Kelley":
                    p = models.Player.objects.get(name="Rob Kelley")
                elif name == "Ted Ginn":
                    p = models.Player.objects.get(name="Ted Ginn Jr.")
                elif name == "Benjamin Watson":
                    p = models.Player.objects.get(name="Ben Watson")
                elif name == "Will Lutz":
                    p = models.Player.objects.get(name="Wil Lutz")
                else:
                    continue
            except models.Player.MultipleObjectsReturned:
                # What to do, what do do use the highest ID?
                p = models.Player.objects.filter(
                    name__iexact=name
                ).order_by(
                    'player_id'
                ).last()

            setattr(p, adp_type, tds[6].text)
            setattr(p, rank_type, tds[0].text)
            p.save()


def populate_franchises(league_id, year):
    inst = Api(year)
    all_players = inst.players(details=True)['players']['player']
    rosters = inst.rosters(league_id)['rosters']['franchise']
    league_info = inst.league(league_id)['league']
    franchises = league_info['franchises']['franchise']
    league = models.League.objects.get(league_id=league_id)
    divisions = league_info['divisions']['division']
    inst = Api(year)
    for division in divisions:
        models.Division.objects.get_or_create(
            division_id=division['id'],
            name=division['name'],
            league=league,
        )
    for roster in rosters:
        r = next((item for item in franchises if item['id'] == roster['id']))
        division = models.Division.objects.get(
            division_id=r['division'],
            league=league,
        )
        f, _ = models.Franchise.objects.get_or_create(
            franchise_id=r['id'],
            division=division,
            league=league,
            defaults={'name': r['name']}
        )
        for player in roster['player']:
            p = next(
                (item for item in all_players if item['id'] == player['id'])
            )
            p['player_id'] = p['id']
            name = p['name'].split(',')
            p['name'] = name[1].strip() + " " + name[0]

            player = models.Player.objects.get(player_id=p['player_id'])
            franchise_player, _ = models.FranchisePlayer.objects.get_or_create(
                franchise=f,
                player=player,
            )


def populate_results(league_id, year):
    instance = Api(year)
    for week in range(17):
        try:
            week = instance.weekly_results(
                league_id, week + 1
            )['weeklyResults']
        except KeyError:
            return

        try:
            matchups = week['matchup']
        except KeyError:
            continue
        if 'franchise' in week:
            # Bye weeks
            for franchise in week['franchise']:
                f = models.Franchise.objects.get(
                    franchise_id=franchise['id'],
                    league__league_id=league_id,
                )
                result, _ = models.Result.objects.update_or_create(
                    franchise=f,
                    week=week['week'],
                    year=year,
                    result='BYE',
                    defaults={
                        'points': franchise['score'],
                    }
                )
                for player in franchise['player']:
                    try:
                        p = models.Player.objects.get(
                            player_id=player['id']
                        )
                    except models.Player.DoesNotExist:
                        continue
                    models.PlayerResult.objects.get_or_create(
                        result=result,
                        player=p,
                        started=player['status'] == 'starter',
                        should_have_started=player['shouldStart'] == '1',
                        available=player['score'] != "",
                        points=player['score'] or 0.0,
                    )

        for matchup in matchups:
            for franchise in matchup['franchise']:
                if 'result' not in franchise:
                    continue
                f = models.Franchise.objects.get(
                    franchise_id=franchise['id'],
                    league__league_id=league_id,
                )
                if franchise['id'] == matchup['franchise'][0]['id']:
                    opponent_id = matchup['franchise'][1]['id']
                else:
                    opponent_id = matchup['franchise'][0]['id']
                opponent = models.Franchise.objects.get(
                    franchise_id=opponent_id,
                    league__league_id=league_id,
                )
                result, _ = models.Result.objects.update_or_create(
                    franchise=f,
                    week=week['week'],
                    year=year,
                    result=franchise['result'],
                    defaults={
                        'opponent': opponent,
                        'points': franchise['score'],
                    }
                )
                for player in franchise['player']:
                    try:
                        p = models.Player.objects.get(
                            player_id=player['id']
                        )
                    except models.Player.DoesNotExist:
                        continue
                    models.PlayerResult.objects.get_or_create(
                        result=result,
                        player=p,
                        available=player['score'] != "",
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
        f = models.Franchise.objects.get(
            franchise_id=franchise['id'],
            league__league_id=league_id,
        )

        for pick in franchise['futureDraftPick']:
            original_franchise = models.Franchise.objects.get(
                franchise_id=pick['originalPickFor'],
                league__league_id=league_id,
            )
            models.Pick.objects.get_or_create(
                draft_year=pick['year'],
                draft_round=pick['round'],
                franchise=original_franchise,
                current_franchise=f,
            )


def populate_trades(league_id, year):
    instance = Api(year)
    trades = instance.transactions(
        league_id, transaction_type="trade"
    )['transactions']['transaction']

    for trade in trades:
        franchise_1 = models.Franchise.objects.get(
            franchise_id=trade['franchise'],
            league__league_id=league_id,
        )
        try:
            offer1 = models.TradeOffer.objects.get(
                franchise=franchise_1,
                trade__timestamp=trade['timestamp'],
                trade__accepted=True,
                is_initiator=True,
            )
            t = offer1.trade
        except models.TradeOffer.DoesNotExist:
            t = models.Trade.objects.create(
                timestamp=trade['timestamp'],
                accepted=True
            )
            offer1 = models.TradeOffer.objects.create(
                franchise=franchise_1,
                trade=t,
                is_initiator=True,
            )

        franchise1_gave_up = trade['franchise1_gave_up'].split(',')[:-1]
        picks = []
        for pick_or_player in franchise1_gave_up:
            if pick_or_player == '':
                continue
            if pick_or_player.startswith('DP'):
                (
                    draft_round,
                    draft_pick,
                ) = pick_or_player.split('_')[1:]
                picks.append("{} {}.{}".format(
                    year,
                    str(int(draft_round) + 1),
                    str(int(draft_pick) + 1),
                ))
            elif pick_or_player.startswith('FP'):
                (
                    franchise_id,
                    draft_year,
                    draft_round,
                ) = pick_or_player.split('_')[1:]
                franchise = models.Franchise.objects.get(
                    franchise_id=franchise_id
                )
                picks.append("{} {} ({})".format(
                    draft_year,
                    draft_round,
                    franchise.name,
                ))
            else:
                player = models.Player.objects.get(
                    player_id=pick_or_player
                )
                offer1.players.add(player)
        offer1.picks = ", ".join(picks)
        offer1.save()
        franchise_2 = models.Franchise.objects.get(
            franchise_id=trade['franchise2'],
            league__league_id=league_id,
        )
        offer2, _ = models.TradeOffer.objects.get_or_create(
            franchise=franchise_2,
            trade=t,
            is_initiator=False,
        )
        franchise2_gave_up = trade['franchise2_gave_up'].split(',')[:-1]
        picks = []
        for pick_or_player in franchise2_gave_up:
            if pick_or_player == '':
                continue
            if pick_or_player.startswith('DP'):
                (
                    draft_round,
                    draft_pick,
                ) = pick_or_player.split('_')[1:]
                picks.append("{} {}.{}".format(
                    year,
                    str(int(draft_round) + 1),
                    str(int(draft_pick) + 1),
                ))
            elif pick_or_player.startswith('FP'):
                (
                    franchise_id,
                    draft_year,
                    draft_round,
                ) = pick_or_player.split('_')[1:]
                franchise = models.Franchise.objects.get(
                    franchise_id=franchise_id
                )
                picks.append("{} {} ({})".format(
                    draft_year,
                    draft_round,
                    franchise.name,
                ))
            else:
                player = models.Player.objects.get(
                    player_id=pick_or_player
                )
                offer2.players.add(player)
        offer2.picks = ", ".join(picks)
        offer2.save()


def populate_auction_draft(league_id, year):
    instance = Api(year)
    draft = instance.auction_results(
        league_id
    )['auctionResults']['auctionUnit']
    for pick in draft['auction']:
        franchise = models.Franchise.objects.get(
            franchise_id=pick['franchise'],
            league__league_id=league_id,
        )

        models.PlayerDraft.objects.get_or_create(
            franchise=franchise,
            player_id=pick['player'],
            timestamp=pick['lastBidTime'],
            defaults={
                'bid_amount': pick['winningBid'],
                'draft_year': year,
            }
        )


def populate_waivers(league_id, year):
    instance = Api(year)
    try:
        blind_waivers = instance.transactions(
            league_id, transaction_type="bbid_waiver"
        )['transactions']['transaction']
    except KeyError:
        return
    for waiver in blind_waivers:
        bought_id, amount, sold_id = waiver['transaction'].split('|')
        bought_id = bought_id.split(',')[0]
        sold_id = sold_id.split(',')[0]
        franchise = models.Franchise.objects.get(
            franchise_id=waiver['franchise'],
            league__league_id=league_id,
        )
        if bought_id:
            models.Waiver.objects.get_or_create(
                franchise=franchise,
                timestamp=waiver['timestamp'],
                player_id=bought_id.split(',')[0],
                amount=int(float(amount)),
                adding=True,
                free_agent=False,
            )
        if sold_id:
            models.Waiver.objects.get_or_create(
                franchise=franchise,
                timestamp=waiver['timestamp'],
                player_id=sold_id.split(',')[0],
                adding=False,
                free_agent=False,
            )
    free_agents = instance.transactions(
        league_id, transaction_type="waiver"
    )['transactions'].get('transaction', [])
    for free_agent in free_agents:
        franchise = models.Franchise.objects.get(
            franchise_id=free_agent['franchise'],
            league__league_id=league_id,
        )
        added = free_agent['added'].split(',')
        for player_id in added:
            if player_id:
                models.Waiver.objects.get_or_create(
                    franchise=franchise,
                    timestamp=free_agent['timestamp'],
                    player_id=player_id,
                    adding=True,
                    free_agent=True,
                )

        dropped = free_agent['dropped'].split(',')
        for player_id in dropped:
            if player_id:
                models.Waiver.objects.get_or_create(
                    franchise=franchise,
                    timestamp=free_agent['timestamp'],
                    player_id=player_id,
                    adding=False,
                    free_agent=True,
                )
