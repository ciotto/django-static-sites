__author__ = 'Christian Bianciotto'


from django.core.management import BaseCommand
from optparse import make_option

from staticsites.deploy import deploy


class Command(BaseCommand):
    help = "Creates all static sites views and deploy new view."

    option_list = BaseCommand.option_list + (
        make_option('--force', '-f', action='store_true', dest='force', default=False,
                    help='Force django-static-files to re-create all files.'),
    )

    def handle(self, deploy_type=None, *args, **options):
        force = options.get('force')

        if deploy_type:
            deploy(deploy_type, force=force)
        else:
            deploy(force=force)




