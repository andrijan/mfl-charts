import json

from django.views.generic import DetailView
from django.views.generic.list import ListView

from . import models


class Franchise(DetailView):
    model = models.Franchise
    pk_url_kwarg = 'franchise_id'

    def get_context_data(self, **kwargs):
        context = super(Franchise, self).get_context_data(**kwargs)
        franchises = models.Franchise.objects.all()
        context['franchises'] = franchises
        players = self.object.players.all().order_by('-total_points')
        adp = players.exclude(
            adp__isnull=True
        ).exclude(
            adp__gt=180
        ).order_by(
            'adp'
        ).values_list(
            'name', 'adp', 'dynasty_adp',
        )
        context['adp'] = json.dumps(list(adp))
        context['players'] = players
        rbs = players.filter(position="RB").values_list(
            'name', 'average_points', 'total_points',
        )
        context['rbs'] = json.dumps(list(rbs))
        wrs = players.filter(position="WR").values_list(
            'name', 'average_points', 'total_points',
        )
        context['wrs'] = json.dumps(list(wrs))
        tes = players.filter(position="TE").values_list(
            'name', 'average_points', 'total_points',
        )
        context['tes'] = json.dumps(list(tes))
        qbs = players.filter(position="QB").values_list(
            'name', 'average_points', 'total_points',
        )
        context['qbs'] = json.dumps(list(qbs))
        context['graph_class'] = 'playerPoints'

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
