import json

from django.db.models import Avg, Max, Min, Q
from django.views.generic import DetailView

from . import models


class FranchiseBase(DetailView):
    model = models.Franchise
    pk_url_kwarg = 'franchise_id'

    def get_context_data(self, **kwargs):
        context = super(FranchiseBase, self).get_context_data(**kwargs)
        franchises = models.Franchise.objects.all()
        context['franchises'] = franchises

        self.players = self.object.players.all().order_by('-total_points')
        context['players'] = self.players
        return context


class PointsPerWeek(FranchiseBase):
    template_name = 'stats/graph.html'

    def get_context_data(self, **kwargs):
        context = super(PointsPerWeek, self).get_context_data(**kwargs)
        results = list(models.Result.objects.filter(
            franchise=self.object
        ).order_by(
            'year', 'week'
        ).values_list(
            'points', flat=True,
        ))
        weeks, averages, maximums, minimums = zip(*list(
            models.Result.objects.values(
                'week', 'year'
            ).order_by(
                'year', 'week'
            ).annotate(
                average=Avg('points'),
                maximum=Max('points'),
                minimum=Min('points'),
            ).values_list(
                'week', 'average', 'maximum', 'minimum',
            )
        ))
        averages = ['%.2f' % avg for avg in averages]
        context['distribution'] = json.dumps(list(zip(
            weeks, results, averages, maximums, minimums
        )))
        context['title'] = 'Points per week'
        context['class'] = 'points'
        context['active'] = 'ppw'

        return context


class PositionBase(FranchiseBase):
    template_name = 'stats/positions.html'

    def get_context_data(self, **kwargs):
        context = super(PositionBase, self).get_context_data(**kwargs)
        players = self.object.players.filter(
            position=self.kwargs['position']
        ).order_by('-total_points')
        context['players'] = players

        partial_players = players.values_list(
            'name', 'average_points', 'total_points',
        )
        context['distribution'] = json.dumps(list(partial_players))
        context['class'] = 'playerPoints'
        context['active'] = self.kwargs['position'].lower()
        return context


class FranchiseAge(FranchiseBase):
    template_name = 'stats/graph.html'

    def get_context_data(self, **kwargs):
        context = super(FranchiseAge, self).get_context_data(**kwargs)
        context['class'] = 'playerAge'
        context['active'] = 'age'
        context['title'] = 'Age distribution'
        context['distribution'] = self.object.age_distribution()
        return context


class FranchiseCollege(FranchiseBase):
    template_name = 'stats/graph.html'

    def get_context_data(self, **kwargs):
        context = super(FranchiseCollege, self).get_context_data(**kwargs)
        context['class'] = 'playerColleges'
        context['active'] = 'colleges'
        context['title'] = 'College distribution'
        context['distribution'] = self.object.college_distribution()
        return context


class FranchiseWeightHeight(FranchiseBase):
    template_name = 'stats/graph.html'

    def get_context_data(self, **kwargs):
        context = super(FranchiseWeightHeight, self).get_context_data(**kwargs)
        context['class'] = 'playerWeightHeight'
        context['active'] = 'wah'
        context['title'] = 'Weight height distribution'
        context['distribution'] = self.object.weight_height_distribution()
        return context


class FranchiseDraftRound(FranchiseBase):
    template_name = 'stats/graph.html'

    def get_context_data(self, **kwargs):
        context = super(FranchiseDraftRound, self).get_context_data(**kwargs)
        context['class'] = 'draftRound'
        context['active'] = 'draft'
        context['title'] = 'Draft Round distribution'
        context['distribution'] = self.object.draft_round_distribution()
        return context


class AverageDraftPosition(FranchiseBase):
    template_name = 'stats/graph.html'

    def get_context_data(self, **kwargs):
        context = super(AverageDraftPosition, self).get_context_data(**kwargs)
        adp = self.players.exclude(
            adp__isnull=True
        ).filter(
            Q(adp__lte=180) | Q(dynasty_adp__lte=180)
        ).order_by(
            'adp'
        ).values_list(
            'name', 'adp', 'dynasty_adp',
        )
        context['title'] = 'ADP'
        context['class'] = 'adp'
        context['active'] = 'adp'
        context['distribution'] = json.dumps(list(adp))
        return context


class Trades(FranchiseBase):
    template_name = 'stats/trades.html'

    def get_context_data(self, **kwargs):
        context = super(Trades, self).get_context_data(**kwargs)
        trade_offers = models.TradeOffer.objects.filter(franchise=self.object)
        context['trades'] = trade_offers
        context['active'] = 'trades'
        return context


class Draft(FranchiseBase):
    template_name = 'stats/draft.html'

    def get_context_data(self, **kwargs):
        context = super(Draft, self).get_context_data(**kwargs)
        players = models.PlayerDraft.objects.filter(franchise=self.object)
        context['drafted_players'] = players
        context['active'] = 'drafted_players'
        return context
