from django.shortcuts import render_to_response, get_object_or_404
from .models import Person, RequestLog
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings


def home(request):
    """
    Returns index page with person's details"""

    person = Person.objects.all().first()
    return render_to_response('hello/index.html', {'person': person})


def requests(request):
    """
    Returns page which displays list of requsts"""

    requests = RequestLog.objects.all()\
                         .order_by('-datetime')[:settings.REQUESTS_ON_PAGE]
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
        .order_by('-datetime')[:settings.REQUESTS_ON_PAGE]
    data = serializers.serialize('json', requests)
    return HttpResponse(data)
