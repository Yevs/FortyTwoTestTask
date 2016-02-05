from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import Person, RequestLog
from .forms import PersonForm
import json
import logging


REQUESTS_ON_PAGE = 10

logger = logging.getLogger(__name__)


def home(request):
    """
    Returns index page with person's details"""

    person = Person.objects.all().order_by('id').first()
    form = PersonForm(instance=person)
    return render(request, 'hello/index.html', {'person': person,
                                                'form': form})


def requests(request):
    """
    Returns page which displays list of requsts"""

    requests = RequestLog.objects.all()\
                         .order_by('-datetime')[:REQUESTS_ON_PAGE]
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
        .order_by('-datetime')[:REQUESTS_ON_PAGE]
    data = [{'datetime': r.datetime.strftime('%d/%m/%Y %H:%M'),
             'method': str(r.method),
             'path': str(r.path),
             'id': str(r.id)} for r in requests]
    return HttpResponse(json.dumps(data))


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
            person = form.save()
            logger.info(u'Successfully submitted form. Fields: {}'.format(
                form.get_fields_str()))
            return HttpResponse(json.dumps({'status': 'ok',
                                            'person': person.get_dict()}))
        else:
            logger.info(u'Form submition failed. Fields: {}.'
                        u' Errors: {}'.format(form.get_fields_str(),
                                              json.dumps(form.errors)))
            return HttpResponse(json.dumps({'status': 'error',
                                            'errors': form.errors}))
    else:
        raise Http404
