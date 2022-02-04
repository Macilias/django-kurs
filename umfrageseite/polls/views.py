from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Poll, Choice


def index(request):
    context = {'umfragen': Poll.objects.all()}
    return render(request=request, template_name='polls/index.html', context=context)


def umfrage_detail(request, slug):
    context = {'umfrage': get_object_or_404(Poll, slug=slug)}
    return render(request=request, template_name='polls/umfrage.html', context=context)


def vote(request, slug):
    umfrage = get_object_or_404(Poll, slug=slug)
    try:
        selected = umfrage.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return HttpResponse("Fehler: es wurde keine bzw. eine ungültige Antwort ausgeählt!")
    else:
        selected.votes += 1
        selected.save()
        return HttpResponseRedirect(reverse('results', args=(umfrage, slug, )))


def results(request, slug):
    context = {'umfrage': get_object_or_404(Poll, slug=slug)}
    return render(request=request, template_name='polls/results.html', context=context)
