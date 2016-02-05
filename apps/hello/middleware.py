from .models import RequestLog


class RequestLoggerMiddleware(object):

    def __init__(self):
        self.IGNORE = ['/api/', '/static/', 'favicon.ico']

    def process_request(self, request):
        for path in self.IGNORE:
            if path in request.path:
                return None
        else:
            RequestLog(method=request.method, path=request.path).save()
