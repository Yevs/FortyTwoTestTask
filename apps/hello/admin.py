from django.contrib import admin
from .models import Person, RequestLog


class RequestAdmin(admin.ModelAdmin):

    list_display = ('path', 'method', 'datetime', 'priority', )
    list_filter = ('priority', )

admin.site.register(Person)
admin.site.register(RequestLog, RequestAdmin)
