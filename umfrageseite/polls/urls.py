from django.urls import path
from .views import index, umfrage_detail

urlpatterns = [
    path('', index, name="index"),
    path('abstimmung/<str:slug>/', umfrage_detail, name="umfrage-detail"),
]