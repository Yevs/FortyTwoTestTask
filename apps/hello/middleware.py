from django.contrib.auth.views import login, logout
from .models import RequestLog
from .views import home, requests


class RequestLoggerMiddleware(object):

    def __init__(self):
        self.VIEWS = [home, requests, login, logout]

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func in self.VIEWS:
            RequestLog(method=request.method, path=request.path).save()
        return None    
