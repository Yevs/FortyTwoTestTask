from django.forms import ModelForm, TextInput, EmailInput, Textarea
from django.forms.widgets import Input
from .models import Person


class Calendar(Input):

    input_type = 'date'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(Calendar, self).__init__(attrs)


class PersonForm(ModelForm):

    class Meta:

        model = Person
        fields = '__all__'
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Name'}),
            'last_name': TextInput(attrs={'class': 'form-control',
                                          'placeholder': 'Last name'}),
            'biography': Textarea(attrs={'class': 'form-control',
                                         'placeholder': 'Your biography...',
                                         'rows': 5}),
            'email': EmailInput(attrs={'class': 'form-control',
                                       'placeholder': 'user@gmail.com'}),
            'skype': TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Skype'}),
            'jabber': TextInput(attrs={'class': 'form-control',
                                       'placeholder': 'Jabber'}),
            'other_contacts': Textarea(attrs={'class': 'form-control',
                                              'placeholder': 'Other contacts',
                                              'rows': 5}),
            'birth_date': Calendar(attrs={'class': 'form-control',
                                          'value': '1990-01-01'}),
        }

    def get_fields_str(self):
        """
        Returns fields of form in form field1: value1, field2: value2, ...
        Used for logging"""

        return u', '.join(u'{}: {}'.format(unicode(field),
                                           unicode(self[field].value()))
                          for field in self.fields if field != 'avatar')
