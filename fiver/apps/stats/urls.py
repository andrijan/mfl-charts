from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^age_distribution/$',
        views.FranchiseAge.as_view(),
        name='franchise_age_distribution',
    ),
    url(
        r'^college_distribution/$',
        views.FranchiseCollege.as_view(),
        name='franchise_college_distribution',
    ),
    url(
        r'^draft_round_distribution/$',
        views.FranchiseDraftRound.as_view(),
        name='franchise_draft_round_distribution',
    ),
    url(
        r'^weight_height_distribution/$',
        views.FranchiseWeightHeight.as_view(),
        name='franchise_weight_height_distribution',
    ),
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
]
