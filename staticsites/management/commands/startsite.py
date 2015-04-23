__author__ = 'Christian Bianciotto'

from os.path import dirname, join

from django.core.management.commands import startapp


class Command(startapp.Command):
    help = ("Creates a Django app directory structure for the given site "
            "name in the current directory or optionally in the given "
            "directory.")

    def handle(self, *args, **options):
        if 'template' not in options or not options['template']:
            options['template'] = join(dirname(dirname(dirname(__file__))), 'templates/site_template')

        super(Command, self).handle(*args, **options)