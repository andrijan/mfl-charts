from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<franchise_id>[\w-]+)/$', views.Franchise.as_view()),
]
