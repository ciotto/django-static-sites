from django.contrib import admin

from models import Deploy
from models import DeployOperation


class DeployAdmin(admin.ModelAdmin):
    # Select visible fields on preview
    list_display = ['id', 'type', 'date']


# Customize DeployOperation admin page.
class DeployOperationAdmin(admin.ModelAdmin):
    # Select visible fields on preview
    list_display = ['id', 'deploy', 'file_type', 'operation_type', 'path', 'hash', 'file_stogare']

admin.site.register(Deploy, DeployAdmin)
admin.site.register(DeployOperation, DeployOperationAdmin)
