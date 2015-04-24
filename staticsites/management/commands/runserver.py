__author__ = 'Christian Bianciotto'


from os.path import join, isfile
from optparse import make_option

from django.utils import autoreload
from django.utils.autoreload import gen_filenames as _gen_filenames
from django.apps import apps
from django.core.management.commands import runserver

from staticsites.deploy import deploy


# Return views.py file of the installed app
def gen_filenames(only_new=False):
    filenames = _gen_filenames(only_new)

    views_files = []

    #TODO add also all templates files

    for app_config in reversed(list(apps.get_app_configs())):
        views_file = join(app_config.path, 'views.py')
        if isfile(views_file):
            views_files.append(views_file)

    return filenames + views_files


class Command(runserver.Command):
    option_list = runserver.Command.option_list + (
        make_option('--autodeploy', '-d', action='store', dest='deploy_type', default=None, nargs=1,
                    help='Tells django-static-sites to autodeploy static pages on change'),
    )

    def run(self, *args, **options):
        """
        Runs the server, using the autoreloader if needed
        """
        use_reloader = options.get('use_reloader')
        deploy_type = options.get('deploy_type')

        if deploy_type:
            deploy(deploy_type)
        else:
            deploy()

        if use_reloader:
            if deploy_type:
                autoreload.gen_filenames = gen_filenames
            autoreload.main(self.inner_run, args, options)
        else:
            self.inner_run(*args, **options)
