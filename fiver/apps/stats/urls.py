from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^age_distribution/$',
        views.FranchiseAge.as_view(),
        name='franshise_age_distribution',
    ),
    url(
        r'^college_distribution/$',
        views.FranchiseCollege.as_view(),
        name='franshise_college_distribution',
    ),
    url(
        r'^draft_round_distribution/$',
        views.FranchiseDraftRound.as_view(),
        name='franshise_draft_round_distribution',
    ),
    url(
        r'^weight_height_distribution/$',
        views.FranchiseWeightHeight.as_view(),
        name='franshise_weight_height_distribution',
    ),
    url(
        r'^(?P<franchise_id>[\w-]+)/$',
        views.Franchise.as_view(),
        name='franshise_details',
    ),
]
