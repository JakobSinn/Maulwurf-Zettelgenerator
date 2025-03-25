from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/
    path("", views.UniqueGremiumListView.as_view(), name="index"),
    path("basisform", views.KandiView),
    path("<str:gremiumwanted>", views.KandiView),
]