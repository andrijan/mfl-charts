from django.core.management.base import BaseCommand
from apps.stats.populate import (
    populate_adp,
    populate_franchises,
    populate_results,
)


class Command(BaseCommand):
    help = 'Populate initial data for the Fiver dynasty league'

    def handle(self, *args, **options):
        populate_franchises(76173, 2017)
        populate_results(76173, 2016)
        populate_adp()
