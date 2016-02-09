from django.forms import ModelForm
from django.forms.widgets import Input
from django import forms
from .models import Person, RequestLog


def get_fields_str(form, exclude=None):
    """
    Returns fields of form in form field1: value1, field2: value2, ...
    Excludes fields that are in exclude.
    Used for logging."""

    if exclude is None:
        exclude = set()
    return u', '.join(u'{}: {}'.format(unicode(field),
                                       unicode(form[field].value()))
                      for field in form.fields if field not in exclude)


class Calendar(Input):

    input_type = 'date'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(Calendar, self).__init__(attrs)


class RequestForm(ModelForm):

    # so blank option would not show up in the html
    method = forms.ChoiceField(choices=RequestLog.METHOD_CHOICES)

    class Meta:

        model = RequestLog
        fields = '__all__'


class PersonForm(ModelForm):

    class Meta:

        model = Person
        fields = '__all__'
        widgets = {
            'birth_date': Calendar()
        }
