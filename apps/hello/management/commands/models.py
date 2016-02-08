from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app

from optparse import make_option


class Command(BaseCommand):

    help = 'Prints all project\'s models and counts number of their objects. '\
           'Use --app to write only hello\'s models and '\
           '--file filename to log to file'

    option_list = BaseCommand.option_list + (
        make_option('--app', default=False, action='store_true', dest='app',
                    help='Uses only hello\'s models'),
        # copys output to file
        make_option('-f', '--file', dest='filename', action='store',
                    type='string', help='log output to file',
                    metavar='FILE'),)

    def handle(self, *args, **options):
        if options['app']:
            models = get_models(get_app('hello'))
        else:
            models = get_models()
        if options['filename']:
            f = open(options['filename'], 'w')
        else:
            f = None
        for model in models:
            name = model.__name__
            count = model.objects.count()
            output = '{} (count: {})'.format(name, count)
            self.stdout.write(output)
            self.stderr.write('error: ' + output)
            if f:
                f.write(output + '\n')
        if f:
            f.close()
