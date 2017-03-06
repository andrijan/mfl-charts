import json

from django.views.generic import DetailView

from . import models


class Franchise(DetailView):
    model = models.Franchise
    pk_url_kwarg = 'franchise_id'

    def get_context_data(self, **kwargs):
        context = super(Franchise, self).get_context_data(**kwargs)
        rbs = self.object.players.filter(position="RB").order_by(
            '-average_points'
        ).values_list(
            'name', 'average_points'
        )
        context['rbs'] = json.dumps(list(rbs))
        wrs = self.object.players.filter(position="WR").order_by(
            '-average_points'
        ).values_list(
            'name', 'average_points'
        )
        context['wrs'] = json.dumps(list(wrs))
        tes = self.object.players.filter(position="TE").order_by(
            '-average_points'
        ).values_list(
            'name', 'average_points'
        )
        context['tes'] = json.dumps(list(tes))
        qbs = self.object.players.filter(position="QB").order_by(
            '-average_points'
        ).values_list(
            'name', 'average_points'
        )
        context['qbs'] = json.dumps(list(qbs))
        context['graph_class'] = 'playerAvgPoints'
        return context
