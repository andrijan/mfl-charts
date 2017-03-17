from datetime import datetime
from django.core.management.base import BaseCommand

from fiver.apps.stats import populate


class Command(BaseCommand):
    help = 'Populate initial data for the Fiver dynasty league'

    def add_arguments(self, parser):
        parser.add_argument('league_id', type=int)
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        league_id = options['league_id']
        year = options['year']
        current_year = datetime.now().year
        for i in range((current_year - year) + 1):
            print("Populate league, year: {}".format(year + i))
            populate.populate_league(league_id, year + i, year)
            print("Populate all players, year: {}".format(year + i))
            populate.populate_all_players(year + i)

        for i in range(current_year - year):
            print("Populate franchises, year: {}".format(year + i))
            populate.populate_franchises(league_id, year + i)
            print("Populate results, year: {}".format(year + i))
            populate.populate_results(league_id, year + i)
            print("Populate picks, year: {}".format(year + i))
            populate.populate_picks(league_id, year + i)
            print("Populate trades, year: {}".format(year + i))
            populate.populate_trades(league_id, year + i)
            print("Populate waivers, year: {}".format(year + i))
            populate.populate_waivers(league_id, year + i)
        print("Populate draft, year: {}".format(year))
        populate.populate_auction_draft(league_id, year)
        print("Populate ADP")
        populate.populate_adp()
