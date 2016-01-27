from django.shortcuts import render_to_response
from .models import Person


def home(request):
    """
    Returns index page with person's details"""

    person = Person.objects.all()[0]
    return render_to_response('hello/index.html', {'person': person})
