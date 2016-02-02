from .models import RequestLog


class RequestLoggerMiddleware(object):

    def process_request(self, request):
        if '/api/' not in request.path and\
           '/static/' not in request.path and\
           'favicon.ico' not in request.path:
            RequestLog(method=request.method, path=request.path).save()
        return None
