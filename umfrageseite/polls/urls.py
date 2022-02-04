from django.urls import path
from .views import index, umfrage_detail, vote

urlpatterns = [
    path('', index, name="index"),
    path('poll/<str:slug>/', umfrage_detail, name="umfrage-detail"),
    path('poll/<str:slug>/vote', vote, name="vote"),
]