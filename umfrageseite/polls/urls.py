from django.urls import path
from .views import index, PollDetailView, vote, ResultsDetailView

app_name = 'polls'
urlpatterns = [
    path('', index, name="index"),
    path('poll/<str:slug>/', PollDetailView.as_view(), name="umfrage-detail"),
    path('poll/<str:slug>/vote/', vote, name="vote"),
    path('poll/<str:slug>/results/', ResultsDetailView.as_view(), name="results"),
]