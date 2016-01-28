from django.shortcuts import render_to_response, get_object_or_404
from .models import Person, RequestLog
from django.utils import simplejson
from django.http import HttpResponse


class JsonResponse(HttpResponse):  # not available in Django 1.6
    """
        JSON response
    """
    def __init__(self, content,
                 mimetype='application/json', status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=simplejson.dumps(content),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )


def home(request):
    """
    Returns index page with person's details"""

    try:
        person = Person.objects.all().first()
        return render_to_response('hello/index.html', {'person': person})
    except IndexError:
        return render_to_response('hello/index.html', {'person': None})


def requests(request):
    """
    Returns page which displays list of requsts"""

    requests = RequestLog.objects.all().order_by('-datetime')[:10]
    return render_to_response('hello/requests.html', {'requests': requests})


def get_requests(request, req_id):
    """
    Returns all requests that happened since last request ordered by datetime.
    If request does not have req_id key then HTTP 400 is returned"""

    request = get_object_or_404(RequestLog, pk=req_id)
    requests = RequestLog.objects.filter(datetime__gt=request.datetime)
    return JsonResponse([{'datetime': r.datetime.strftime('%d/%m/%Y %H:%M'),
                          'method': str(r.method),
                          'path': str(r.path)} for r in requests])
