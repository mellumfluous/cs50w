from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:id>", views.wiki, name="wiki"),
    path('search', views.search, name='search')
]
