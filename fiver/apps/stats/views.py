import json

from django.views.generic import DetailView

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
