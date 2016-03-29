__author__ = 'Christian Bianciotto'


from os.path import join, isfile
from optparse import make_option

from django.utils import autoreload
from django.utils.autoreload import gen_filenames as _gen_filenames
from django.apps import apps
from django.contrib.staticfiles.management.commands import runserver

from staticsites.deploy import deploy
from staticsites import utilities


# Return also all file of the installed app
def gen_filenames(only_new=False):
    filenames = _gen_filenames(only_new)

    apps_files = []

    def add_files(path, sub_path, *args, **kwargs):
        full_path = join(path, sub_path)
        if isfile(full_path):
            apps_files.append(full_path)

    for app_config in reversed(list(apps.get_app_configs())):
        ignore = utilities.get_conf('STATICSITE_IGNORE', deploy_type=autoreload.deploy_type)
        utilities.iterate_dir(app_config.path, add_files, ignore)

    return filenames + apps_files


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
                autoreload.deploy_type = deploy_type
                autoreload.gen_filenames = gen_filenames
            autoreload.main(self.inner_run, args, options)
        else:
            self.inner_run(*args, **options)

    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
