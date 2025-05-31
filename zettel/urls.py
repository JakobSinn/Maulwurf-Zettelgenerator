from django.urls import path

from . import views

urlpatterns = [
    path("", views.UniqueGremiumListView.as_view(), name="index"),
    path("basisform", views.KandiView, name ="leer"),
    path("gremium/<path:gremiumwanted>", views.KandiView, name="kandidaturen"),
]
