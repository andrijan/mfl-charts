import json

from django.db.models import Avg, Max, Min, Q
from django.views.generic import DetailView
from django.views.generic.list import ListView

from . import models


class FranchiseBase(DetailView):
    model = models.Franchise
    pk_url_kwarg = 'franchise_id'

    def get_context_data(self, **kwargs):
        context = super(FranchiseBase, self).get_context_data(**kwargs)
        franchises = models.Franchise.objects.all()
        context['franchises'] = franchises

        players = self.object.players.all().order_by('-total_points')
        adp = players.exclude(
            adp__isnull=True
        ).filter(
            Q(adp__lte=180) | Q(dynasty_adp__lte=180)
        ).order_by(
            'adp'
        ).values_list(
            'name', 'adp', 'dynasty_adp',
        )
        context['adp'] = json.dumps(list(adp))
        context['players'] = players
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
        return context


class FranchiseAge(ListView):
    model = models.Franchise
    template_name = 'stats/graphs.html'
    context_object_name = 'franchises'

    def get_context_data(self, **kwargs):
        context = super(FranchiseAge, self).get_context_data(**kwargs)
        context['graph_class'] = 'playerAge'
        context['title'] = 'Age distribution'
        context['function'] = 'age_distribution'
        context['getattr'] = getattr
        context['position'] = self.request.GET.get('position', None)
        return context


class FranchiseCollege(ListView):
    model = models.Franchise
    template_name = 'stats/graphs.html'
    context_object_name = 'franchises'

    def get_context_data(self, **kwargs):
        context = super(FranchiseCollege, self).get_context_data(**kwargs)
        context['graph_class'] = 'playerColleges'
        context['title'] = 'College distribution'
        context['function'] = 'college_distribution'
        context['getattr'] = getattr
        context['position'] = self.request.GET.get('position', None)
        return context


class FranchiseDraftRound(ListView):
    model = models.Franchise
    template_name = 'stats/graphs.html'
    context_object_name = 'franchises'

    def get_context_data(self, **kwargs):
        context = super(FranchiseDraftRound, self).get_context_data(**kwargs)
        context['graph_class'] = 'draftRound'
        context['title'] = 'Draft Round distribution'
        context['function'] = 'draft_round_distribution'
        context['getattr'] = getattr
        context['position'] = self.request.GET.get('position', None)
        return context


class FranchiseWeightHeight(ListView):
    model = models.Franchise
    template_name = 'stats/graphs.html'
    context_object_name = 'franchises'

    def get_context_data(self, **kwargs):
        context = super(FranchiseWeightHeight, self).get_context_data(**kwargs)
        context['graph_class'] = 'playerWeightHeight'
        context['title'] = 'Weight height distribution'
        context['function'] = 'weight_height_distribution'
        context['getattr'] = getattr
        context['position'] = self.request.GET.get('position', None)
        return context
