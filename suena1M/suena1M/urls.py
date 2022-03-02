"""suena1M URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import (
    index,
    game,
    new_game,
    start_game,
    register,
    ResultsDetailView,
)

app_name = "suena1M"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),
    path("", index, name="index"),
    path("/new_game/", new_game, name="new_game"),
    path("<str:slug>/", game, name="game"),
    path("<str:slug>/start_game/", start_game, name="start_game"),
    path("<str:slug>/register/", register, name="register"),
    path("<str:slug>/results/", ResultsDetailView.as_view(), name="results"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
