from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core import serializers
from django.conf import settings

from .models import Person, RequestLog
from .forms import PersonForm
import json


def home(request):
    """
    Returns index page with person's details"""

    person = Person.objects.all().order_by('id').first()
    return render(request, 'hello/index.html', {'person': person})


def requests(request):
    """
    Returns page which displays list of requsts"""

    requests = RequestLog.objects.all()\
                         .order_by('-datetime')[:settings.REQUESTS_ON_PAGE]
    last_req_id = requests[0].id
    return render(request, 'hello/requests.html',
                           {'requests': requests,
                            'last_req_id': last_req_id})


def get_requests(request, req_id):
    """
    Returns all requests that happened since last request ordered by datetime.
    If request does not have req_id key then HTTP 404 is returned"""

    req = get_object_or_404(RequestLog, pk=req_id)
    requests = RequestLog.objects.filter(datetime__gt=req.datetime)\
        .order_by('-datetime')[:settings.REQUESTS_ON_PAGE]
    data = serializers.serialize('json', requests)
    return HttpResponse(data)


@login_required
def edit(request):
    """
    Returns edit page on GET
    Validates data and saves changes on POST"""

    if Person.objects.count() == 0:
        raise Http404
    if request.method == 'GET':
        form = PersonForm(instance=Person.objects.first())
        return render(request, 'hello/form.html', {'form': form})
    elif request.method == 'POST':
        form = PersonForm(request.POST, instance=Person.objects.first())
        if form.is_valid():
            form.save()
        return redirect(reverse('hello:home'))
    else:
        raise Http404


@login_required
def edit_api(request):
    """
    Processes json to update Person object"""

    if Person.objects.count() == 0:
        raise Http404
    if request.method == 'POST':
        form = PersonForm(data=request.POST, files=request.FILES,
                          instance=Person.objects.first())
        if form.is_valid():
            form.save()
            return HttpResponse('{"status": "ok"}')
        else:
            return HttpResponse(json.dumps({'status': 'error',
                                            'errors': form.errors}))
    else:
        raise Http404


def login(request):
    """
    Returns login page on GET
    Logins a user on POST"""

    if request.user.is_authenticated():
        return redirect(reverse('hello:home'))
    if request.method == 'GET':
        form = AuthenticationForm(request)
        form.fields['username'].widget.attrs['class'] = 'form-control'
        form.fields['password'].widget.attrs['class'] = 'form-control'
        return render(request, 'hello/login.html', {'form': form})
    elif request.method == 'POST':
        form = AuthenticationForm(request, request.POST or None)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(reverse('hello:home'))
        else:
            return render(request, 'hello/login.html', {'form': form})
    else:
        raise Http404


@login_required
def logout(request):
    """
    Logs user out"""

    auth_logout(request)
    return redirect(reverse('hello:home'))
