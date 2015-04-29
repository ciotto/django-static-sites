__author__ = 'Christian Bianciotto'


from genericpath import exists
from os import makedirs
from os.path import abspath
from datetime import datetime
from staticsites import utilities
import hashlib
import logging
import io

from inspect import getmembers, isfunction
from django.utils import importlib
from django.conf import settings
from django.utils.module_loading import import_module
from django.db.models import Q
from django.http import HttpRequest

from models import DeployOperation, Deploy


def deploy(deploy_type=utilities.get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')):
    logging.basicConfig(
        level=logging.DEBUG,
        format='(%(threadName)-10s) %(message)s',
    )

    dp = Deploy(type=deploy_type)
    dp.save()

    utilities.set_settings(deploy_type)

    paths = []

    # Create deploy root
    deploy_root = utilities.get_deploy_root(deploy_type)
    if not exists(deploy_root):
        makedirs(deploy_root)

    # Copy static files
    staticfiles_dirs = utilities.get_conf('STATICSITE_STATICFILES_DIRS', deploy_type)
    if staticfiles_dirs:
        if isinstance(staticfiles_dirs, basestring):
            raise AssertionError("type %s is not iterable" % type(staticfiles_dirs))

        for staticfiles_dir in staticfiles_dirs:
            if isinstance(staticfiles_dir, basestring):
                raise AssertionError("type %s is not iterable" % type(staticfiles_dir))

            path = abspath(staticfiles_dir[0])
            if len(staticfiles_dir) > 1:
                file_storage = staticfiles_dir[1]
                file_storage = utilities.get_file_storage(file_storage, deploy_type)
            else:
                file_storage = utilities.get_file_storage(None, deploy_type)

            storage = file_storage(deploy_root)

            utilities.iterate_dir(path, utilities.copy_file, None, storage, dp, paths)

    # Create dynamic files
    for appname in settings.INSTALLED_APPS:
        if appname != 'staticsites':
            try:
                views = import_module(appname + '.views')

                for func_name, function in getmembers(views, isfunction):
                    if hasattr(function, 'is_static_view') and function.is_static_view:
                        path = function.path
                        minify = function.minify
                        gzip = function.gzip
                        file_storage = function.file_storage

                        path = utilities.get_path(path, func_name, deploy_type)
                        minify = utilities.get_minify(minify, path, deploy_type)
                        gzip = utilities.get_gzip(gzip, deploy_type)
                        file_storage = utilities.get_file_storage(file_storage, deploy_type)

                        if 'deploy_type' in function.func_code.co_varnames:
                            response = function(HttpRequest(), deploy_type)
                        else:
                            response = function(HttpRequest())

                        storage = file_storage(deploy_root)

                        content = response.content

                        new_dpo = DeployOperation(deploy=dp,
                                                  file_type='D',
                                                  operation_type='N',
                                                  path=path,
                                                  md5=hashlib.md5(content).hexdigest(),
                                                  file_stogare=storage.__class__.__module__ + '.' + storage.__class__.__name__)

                        skip = False

                        if storage.exists(path):
                            # Check if need update by checking stored md5
                            md5 = None
                            deploy_operations = DeployOperation.objects.filter(path=path, deploy__type=deploy_type).reverse()
                            if deploy_operations:
                                md5 = deploy_operations[0].md5

                            if not md5 or new_dpo.md5 != md5:
                                storage.delete(path)
                                new_dpo.operation_type = 'U'
                            else:
                                new_dpo.operation_type = 'NU'
                                logging.info('File %s not updated' % path)

                        if new_dpo.operation_type is not 'NU':
                            file = None
                            try:
                                file = io.BytesIO(response.content)
                                storage.save(path, file)

                                if new_dpo.operation_type is 'U':
                                    logging.info('Update file %s' % path)
                                else:
                                    logging.info('Create dynamic file %s' % path)
                            finally:
                                if file:
                                    file.close()

                        new_dpo.save()

                        paths.append(path)
            except ImportError:
                logging.info('No views module for app %s' % appname)

    # Clean files
    deploys = Deploy.objects.exclude(id=dp.id).order_by('-id')
    if len(deploys):
        last_dp = deploys[0]
        removed_paths = DeployOperation.objects.filter(deploy=last_dp).exclude(Q(path__in=paths) | Q(operation_type='R'))
        for path in removed_paths:
            file_stogare_components = path.file_stogare.rsplit('.', 1)
            file_storage = getattr(importlib.import_module(file_stogare_components[0]), file_stogare_components[1])
            storage = file_storage(deploy_root)
            storage.delete(path.path)
            new_dpo = DeployOperation(deploy=dp,
                                      file_type=path.file_type,
                                      operation_type='R',
                                      path=path.path,
                                      md5=path.md5,
                                      file_stogare=path.file_stogare)
            new_dpo.save()
