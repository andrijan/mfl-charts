import json

from operator import itemgetter

from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.views.generic import DetailView
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView

from . import models


class DraftBoard(ListView):
    model = models.Player
    template_name = 'stats/draft_board.html'

    def get_queryset(self):
        qs = super(DraftBoard, self).get_queryset()
        return qs.filter(rank__lte=300)


class FranchiseRedirect(RedirectView):
    @property
    def pattern_name(self):
        return self.kwargs['url_name']

    def get_redirect_url(self, *args, **kwargs):
        kwargs.pop('url_name')
        url = super(FranchiseRedirect, self).get_redirect_url(*args, **kwargs)
        return url


class FranchiseBase(DetailView):
    model = models.Franchise
    pk_url_kwarg = 'franchise_id'

    def get_context_data(self, **kwargs):
        context = super(FranchiseBase, self).get_context_data(**kwargs)
        franchises = models.Franchise.objects.all()
        context['franchises'] = franchises
        self.players = self.object.franchise_players.order_by(
            '-points__total_points'
        )
        return context


class TopPlayers(FranchiseBase):
    def get_context_data(self, **kwargs):
        context = super(TopPlayers, self).get_context_data(**kwargs)

        context['players'] = self.players
        context['active'] = 'players'
        return context


class TaxiEligibility(TopPlayers):
    template_name = 'stats/taxi_eligibility.html'

    def get_context_data(self, **kwargs):
        context = super(TaxiEligibility, self).get_context_data(**kwargs)

        context['active'] = 'positions'
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
        players = models.PlayerResult.objects.filter(
            player__position=self.kwargs['position'],
            player__franchise_player__franchise=self.object,
            available=True,
        ).values(
            'player_id',
            'started',
        ).annotate(
            Count('started'),
        ).values(
            'player_id',
            'player__name',
        ).annotate(
            total_points=Sum('points'),
            average_points=Avg('points'),
            games=Count('points'),
        ).order_by(
            '-total_points'
        )
        players_list = []
        for player in players:
            players_dict = {}
            for key, value in player.items():
                players_dict[key] = value
            players_dict['player'] = models.Player.objects.get(
                player_id=player['player_id']
            )
            players_list.append(players_dict)

        context['players'] = players_list

        distribution = []
        for player in players:
            distribution.append([
                player['player__name'],
                player['average_points'],
                player['total_points'],
            ])

        context['distribution'] = json.dumps(distribution)
        context['class'] = 'playerPoints'
        context['active'] = 'positions'
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
            player__adp__isnull=True
        ).filter(
            Q(player__adp__lte=180) | Q(player__dynasty_adp__lte=180)
        ).order_by(
            'player__rank'
        ).values_list(
            'player__name', 'player__rank', 'player__dynasty_rank',
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


class Waivers(FranchiseBase):
    template_name = 'stats/waivers.html'

    def get_context_data(self, **kwargs):
        context = super(Waivers, self).get_context_data(**kwargs)
        waivers = models.Waiver.objects.filter(franchise=self.object)
        context['waivers'] = waivers
        context['active'] = 'waivers'
        return context


class Player(DetailView):
    model = models.FranchisePlayer
    pk_url_kwarg = 'player_id'

    def get_object(self, queryset=None):
        return models.FranchisePlayer.objects.get(
            player__player_id=self.kwargs.get('player_id'),
            franchise__league__league_id=self.kwargs.get('league_id'),
        )

    def get_context_data(self, **kwargs):
        context = super(Player, self).get_context_data(**kwargs)
        franchises = models.Franchise.objects.all()
        context['franchises'] = franchises
        history = []
        for draft in self.object.player.drafts.all():
            history.append({
                'type': 'Draft',
                'date': draft.date,
                'franchise': draft.franchise,
                'amount': draft.bid_amount
            })
        for trade in self.object.player.trades.filter(trade__accepted=True):
            history.append({
                'type': 'Trade',
                'date': trade.date,
                'franchise': trade.other_franchise.franchise,
                'amount': {
                    'giving_up': trade.giving_up,
                    'receiving': trade.receiving,
                }
            })
        for waiver in self.object.player.waivers.all():
            history.append({
                'type': 'Add' if waiver.adding else 'Drop',
                'date': waiver.date,
                'franchise': waiver.franchise,
                'amount': "FA" if waiver.free_agent else waiver.amount
            })
        history.sort(key=itemgetter('date'))
        context['history'] = history
        return context
