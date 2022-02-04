from django.urls import path
from .views import index, umfrage_detail

urlpatterns = [
    path('', index),
    path('abstimmung/<str:slug>/', umfrage_detail),
]