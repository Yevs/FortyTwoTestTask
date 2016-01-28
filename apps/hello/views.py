from django.shortcuts import render_to_response
from .models import Person


def home(request):
    """
    Returns index page with person's details"""

    try:
        person = Person.objects.all().first()
        return render_to_response('hello/index.html', {'person': person})
    except IndexError:
        return render_to_response('hello/index.html', {'person': None})
