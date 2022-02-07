from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .models import Poll, Choice


def index(request):
    context = {'umfragen': Poll.objects.all()}
    return render(request=request, template_name='polls/index.html', context=context)


class PollDetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/umfrage.html'


class ResultsDetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'


def vote(request, slug):
    umfrage = get_object_or_404(Poll, slug=slug)
    try:
        selected = umfrage.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return HttpResponse("Fehler: es wurde keine bzw. eine ungültige Antwort ausgeählt!")
    else:
        selected.votes += 1
        selected.save()
        return HttpResponseRedirect(reverse('results', args=(umfrage.slug,)))
