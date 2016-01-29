from django.contrib import admin
from .models import Person, RequestLog


class PersonAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        """
        Adding is permitted only when there is only one person in db"""

        return self.model.objects.count() == 0

admin.site.register(Person, PersonAdmin)
admin.site.register(RequestLog)
