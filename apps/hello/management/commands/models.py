from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app

from optparse import make_option


class Command(BaseCommand):

    help = 'Prints all project\'s models and counts number of their objects'

    option_list = BaseCommand.option_list + (
        make_option('--app', default=False, action='store_true', dest='app',
                    help='Uses only hello\'s models'),)

    def handle(self, *args, **options):
        if options['app']:
            models = get_models(get_app('hello'))
        else:
            models = get_models()
        for model in models:
            name = model.__name__
            count = model.objects.count()
            self.stdout.write('{} (count: {})'.format(name, count))
