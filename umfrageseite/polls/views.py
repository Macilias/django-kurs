from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Poll


def index(request):
    context = {'umfragen': Poll.objects.all()}
    return render(request=request, template_name='polls/index.html', context=context)


def umfrage_detail(request, slug):
    context = {'umfrage': get_object_or_404(Poll, slug=slug)}
    return render(request=request, template_name='polls/umfrage.html', context=context)
