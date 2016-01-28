from django.contrib import admin
from .models import Person, RequestLog


admin.site.register(Person)
admin.site.register(RequestLog)
