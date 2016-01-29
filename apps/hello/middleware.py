from .models import RequestLog
from django.utils import timezone


class RequestLoggerMiddleware(object):

    def process_request(self, request):
        RequestLog(datetime=timezone.now(),
                   method=request.method, path=request.path).save()
        return None
