from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.conf import settings
from django.db.models import Max
from .models import Person, RequestLog
from .forms import PersonForm, RequestForm, get_fields_str
import json
import logging


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

    requests = RequestLog.objects.all().order_by('-datetime', '-priority')
    requests = requests[:settings.REQUESTS_ON_PAGE]
    last_req_id = requests[0].id
    max_prior = RequestLog.objects.all()\
        .aggregate(Max('priority'))['priority__max']
    return render(request, 'hello/requests.html',
                           {'requests': requests,
                            'last_req_id': last_req_id,
                            'max_prior': max_prior})


@login_required
def request_edit(request, req_id):
    """
    Returns page with form to edit request on GET.
    Validates form and redirects to /requests/ on POST."""

    req = get_object_or_404(RequestLog, pk=req_id)
    if request.method == 'GET':
        form = RequestForm(instance=req)
        return render(request, 'hello/request_edit.html', {'form': form})
    elif request.method == 'POST':
        form = RequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            logger.info(u'Successfully submitted request form. '
                        u'Fields: {}'.format(get_fields_str(form)))
            return redirect(reverse('hello:requests'))
        else:
            logger.info(u'Request form submition failed. Fields: {}.'
                        u' Errors: {}'.format(get_fields_str(form),
                                              json.dumps(form.errors)))
            return render(request,
                          'hello/request_edit.html',
                          {'form': form})
    raise Http404


def parse_args(args):
    """
    Parses arguments for requests api functions"""

    count = int(args.get('count', settings.REQUESTS_ON_PAGE))
    lower = int(args.get('lower', 0))
    upper = int(args.get('upper', 2147483647))  # max value
    order = 'time'
    if 'order' in args:
        if args['order'].strip() == 'priority':
            order = 'priority'
    return count, lower, upper, order


def get_requests_by_args(count, lower, upper, order, datetime=None):
    """
    Returns requests from db that satisfy order"""

    if order == 'time':
        ordering = ('-datetime', '-priority')
    else:
        ordering = ('-priority', '-datetime')
    filters = {
        'priority__gte': lower,
        'priority__lte': upper
    }
    if datetime:
        filters['datetime__gt'] = datetime
    requests = RequestLog.objects.filter(**filters).order_by(*ordering)
    return requests[:count]


def get_requests(request):
    """
    Returns requests that satisfy request in json format"""

    if request.method == 'GET':
        try:
            requests = get_requests_by_args(*parse_args(request.GET))
            return HttpResponse(serializers.serialize('json', requests))
        except ValueError:
            message = 'Parameters supposed to be int turned out not being int'
            response = HttpResponse(message)
            response.status_code = 422
            return response
    else:
        raise Http404


def get_last_requests(request, req_id):
    """
    Returns all requests that happened since last request ordered by datetime.
    If request does not have req_id key then HTTP 404 is returned"""

    req = get_object_or_404(RequestLog, pk=req_id)
    requests = get_requests_by_args(*parse_args(request.GET),
                                    datetime=req.datetime)
    data = serializers.serialize('json', requests)
    return HttpResponse(data)


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
                get_fields_str(form, {'avatar'})))
            return HttpResponse(json.dumps({'status': 'ok',
                                            'person': person.get_dict()}))
        else:
            logger.info(u'Form submition failed. Fields: {}.'
                        u' Errors: {}'.format(get_fields_str(form, {'avatar'}),
                                              json.dumps(form.errors)))
            return HttpResponse(json.dumps({'status': 'error',
                                            'errors': form.errors}))
    else:
        raise Http404
