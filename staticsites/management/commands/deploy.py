__author__ = 'Christian Bianciotto'


from django.core.management import BaseCommand

from staticsites.deploy import deploy


class Command(BaseCommand):
    help = "Creates all static sites views and deploy new view."

    def handle(self, deploy_type=None, *args, **options):
        if deploy_type:
            deploy(deploy_type)
        else:
            deploy()




