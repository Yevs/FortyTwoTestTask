from datetime import datetime
from .models import RequestLog


class RequestLoggerMiddleware(object):

    def process_request(self, request):
        RequestLog(datetime=datetime.now(),
                   method=request.method, path=request.path).save()
        return None
