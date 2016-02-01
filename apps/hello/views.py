from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from .models import Person, RequestLog
from .forms import PersonForm
import json


REQUESTS_ON_PAGE = 10


def home(request):
    """
    Returns index page with person's details"""

    person = Person.objects.all().order_by('id').first()
    return render_to_response('hello/index.html', {'person': person})


def requests(request):
    """
    Returns page which displays list of requsts"""

    requests = RequestLog.objects.all()\
                         .order_by('-datetime')[:REQUESTS_ON_PAGE]
    last_req_id = requests[0].id
    return render_to_response('hello/requests.html',
                              {'requests': requests,
                               'last_req_id': last_req_id})


def get_requests(request, req_id):
    """
    Returns all requests that happened since last request ordered by datetime.
    If request does not have req_id key then HTTP 404 is returned"""

    req = get_object_or_404(RequestLog, pk=req_id)
    requests = RequestLog.objects.filter(datetime__gt=req.datetime)\
        .order_by('-datetime')[:REQUESTS_ON_PAGE]
    data = [{'datetime': r.datetime.strftime('%d/%m/%Y %H:%M'),
             'method': str(r.method),
             'path': str(r.path),
             'id': str(r.id)} for r in requests]
    return HttpResponse(json.dumps(data))


def edit(request):
    """
    Returns edit page on GET
    Validates data and saves changes on POST"""

    if Person.objects.count() == 0:
        raise Http404
    if request.method == 'GET':
        form = PersonForm(instance=Person.objects.first())
        return render_to_response('hello/form.html', {'form': form})
    elif request.method == 'POST':
        form = PersonForm(request.POST, instance=Person.objects.first())
        if form.is_valid():
            form.save()
        return redirect(reverse('hello:home'))
    else:
        raise Http404


def edit_api(request):
    """
    Processes json to update Person object"""

    if Person.objects.count() == 0:
        raise Http404
    if request.method == 'POST':
        print(request.POST, request.FILES);
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
