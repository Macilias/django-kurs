from django.shortcuts import render
from django.http import HttpResponse
from .models import Poll


def index(request):
    result = ''
    for poll in Poll.objects.all():
        result += ' </br> '
        result += f'{poll.name} ({", ".join(str(x.name) for x in poll.choice_set.all()) })'

    return HttpResponse(result)
