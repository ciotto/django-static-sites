__author__ = 'Christian Bianciotto'

from os.path import dirname, join

from django.core.management.commands import startproject


class Command(startproject.Command):
    help = ("Creates a Django project directory structure optimised for static site "
            "for the given project name in the current directory or optionally in the "
            "given directory.")

    def handle(self, *args, **options):
        if 'template' not in options or not options['template']:
            options['template'] = join(dirname(dirname(dirname(__file__))), 'templates/project_template')

        super(Command, self).handle(*args, **options)
