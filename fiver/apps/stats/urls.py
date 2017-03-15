from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^(?P<franchise_id>[\w-]+)/$',
        views.FranchiseBase.as_view(),
        name='franchise_details',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/points_per_week/$',
        views.PointsPerWeek.as_view(),
        name='franchise_points_per_week',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/position/(?P<position>[\w-]+)/$',
        views.PositionBase.as_view(),
        name='franchise_positions',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/age/$',
        views.FranchiseAge.as_view(),
        name='franchise_age',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/college/$',
        views.FranchiseCollege.as_view(),
        name='franchise_college',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/weight_height/$',
        views.FranchiseWeightHeight.as_view(),
        name='franchise_weight_height',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/draft_round/$',
        views.FranchiseDraftRound.as_view(),
        name='franchise_draft_round',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/adp/$',
        views.AverageDraftPosition.as_view(),
        name='franchise_adp',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/trades/$',
        views.Trades.as_view(),
        name='franchise_trades',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/draft/$',
        views.Draft.as_view(),
        name='franchise_draft',
    ),
]
