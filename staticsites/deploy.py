__author__ = 'Christian Bianciotto'


from StringIO import StringIO
from gzip import GzipFile

from genericpath import exists
from os import makedirs
from os.path import abspath, join, getmtime
from staticsites import utilities
from datetime import datetime
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


class DefaultDeployUtilities:
    def __init__(self, deploy_type):
        self.deploy_type = deploy_type
        self.deploy = None
        self.storage = None

        self.paths = []
        self.deploy_operations = []

    def copy(self, path, sub_path):
        full_path = join(path, sub_path)

        minify = utilities.get_minify(None, sub_path, self.deploy_type)

        gzip = utilities.get_gzip(None, self.deploy_type)

        file = None
        try:
            operation_type = 'N'

            if self.storage.exists(sub_path):
                # Check if need update by checking modification date
                if datetime.fromtimestamp(getmtime(full_path)) > self.storage.modified_time(sub_path):
                    self.storage.delete(sub_path)
                    operation_type = 'U'
                else:
                    operation_type = 'NU'
                    logging.info('File %s not updated' % path)

            if operation_type is not 'NU':
                if minify or gzip:
                    if minify:
                        content = utilities.read_file(full_path)
                        content = minify(content)
                    else:
                        content = utilities.read_binary(full_path)

                    if gzip:
                        #TODO gzip config discriminate extension
                        #TODO append .gz extension (config)
                        file = StringIO()
                        gzip_file = GzipFile(fileobj=file, mode="w")
                        gzip_file.write(content)
                        gzip_file.close()
                    else:
                        file = io.StringIO(content)
                else:
                    file = open(full_path, 'r')
                self.storage.save(sub_path, file)

                if operation_type is 'U':
                    logging.info('Update file %s' % sub_path)
                else:
                    logging.info('Create dynamic file %s' % sub_path)

            dpo = DeployOperation(deploy=self.deploy,
                                  file_type='S',
                                  operation_type=operation_type,
                                  path=sub_path,
                                  file_stogare=self.storage.__class__.__module__ + '.' +
                                               self.storage.__class__.__name__)
            dpo.save()

            if sub_path not in self.paths:
                self.paths.append(sub_path)
            self.deploy_operations.append(dpo)
        finally:
            if file:
                file.close()

    def start(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='(%(threadName)-10s) %(message)s',
        )

        deploys = Deploy.objects.filter(type=self.deploy_type).order_by('-id')
        last_dp = None
        if len(deploys):
            last_dp = deploys[0]

        self.deploy = Deploy(type=self.deploy_type)
        self.deploy.save()

        before_deploy = utilities.get_conf('STATICSITE_BEFORE_DEPLOY', self.deploy_type)
        after_deploy = utilities.get_conf('STATICSITE_AFTER_DEPLOY', self.deploy_type)

        if before_deploy:
            before_deploy(deploy_type=self.deploy_type, deploy=self.deploy)

        utilities.set_settings(self.deploy_type)

        # Create deploy root
        deploy_root = utilities.get_deploy_root(self.deploy_type)
        if not exists(deploy_root):
            makedirs(deploy_root)

        # Copy static files
        staticfiles_dirs = utilities.get_conf('STATICSITE_STATICFILES_DIRS', self.deploy_type)
        if staticfiles_dirs:
            if isinstance(staticfiles_dirs, basestring):
                raise AssertionError("type %s is not iterable" % type(staticfiles_dirs))

            for staticfiles_dir in staticfiles_dirs:
                if isinstance(staticfiles_dir, basestring):
                    raise AssertionError("type %s is not iterable" % type(staticfiles_dir))

                path = abspath(staticfiles_dir[0])
                if len(staticfiles_dir) > 1:
                    file_storage = staticfiles_dir[1]
                    storages = utilities.get_storages(file_storage=file_storage,
                                                    deploy_type=self.deploy_type,
                                                    location=deploy_root)
                else:
                    storages = utilities.get_storages(file_storage=None,
                                                    deploy_type=self.deploy_type,
                                                    location=deploy_root)

                for storage in storages:
                    self.storage = storage
                    utilities.iterate_dir(path, self.copy)

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

                            path = utilities.get_path(path, func_name, self.deploy_type)
                            minify = utilities.get_minify(minify, path, self.deploy_type)
                            gzip = utilities.get_gzip(gzip, self.deploy_type)

                            if 'deploy_type' in function.func_code.co_varnames:
                                response = function(HttpRequest(), self.deploy_type)
                            else:
                                response = function(HttpRequest())

                            storages = utilities.get_storages(file_storage=file_storage,
                                                            deploy_type=self.deploy_type,
                                                            location=deploy_root)

                            content = response.content

                            for storage in storages:
                                self.storage = storage
                                new_dpo = DeployOperation(deploy=self.deploy,
                                                          file_type='D',
                                                          operation_type='N',
                                                          path=path,
                                                          hash=hashlib.sha512(content).hexdigest(),
                                                          file_stogare=self.storage.__class__.__module__ + '.' +
                                                                       self.storage.__class__.__name__)

                                if storage.exists(path):
                                    # Check if need update by checking stored hash
                                    last_dpo = None
                                    if last_dp:
                                        deploy_operations = DeployOperation.objects.filter(path=path, deploy=last_dp)
                                        if deploy_operations:
                                            last_dpo = deploy_operations[0]

                                    if last_dpo and last_dpo.hash and new_dpo.hash == last_dpo.hash:
                                        new_dpo.operation_type = 'NU'
                                        logging.info('File %s not updated' % path)
                                    else:
                                        storage.delete(path)
                                        new_dpo.operation_type = 'U'

                                if new_dpo.operation_type is not 'NU':
                                    file = None
                                    try:
                                        file = io.BytesIO(content)
                                        storage.save(path, file)

                                        if new_dpo.operation_type is 'U':
                                            logging.info('Update file %s' % path)
                                        else:
                                            logging.info('Create dynamic file %s' % path)
                                    finally:
                                        if file:
                                            file.close()

                                new_dpo.save()
                                self.deploy_operations.append(new_dpo)

                            if path not in self.paths:
                                self.paths.append(path)
                except ImportError:
                    logging.info('No views module for app %s' % appname)

        # Clean files
        if last_dp:
            removed_paths = DeployOperation.objects.filter(deploy=last_dp).exclude(Q(path__in=self.paths) | Q(operation_type='R'))
            for path in removed_paths:
                file_stogare_components = path.file_stogare.rsplit('.', 1)
                file_storage = getattr(importlib.import_module(file_stogare_components[0]), file_stogare_components[1])
                storage = file_storage(deploy_root)
                storage.delete(path.path)
                new_dpo = DeployOperation(deploy=self.deploy,
                                          file_type=path.file_type,
                                          operation_type='R',
                                          path=path.path,
                                          hash=path.hash,
                                          file_stogare=path.file_stogare)
                new_dpo.save()
                self.deploy_operations.append(new_dpo)
                if path not in self.paths:
                    self.paths.append(path)

        if after_deploy:
            after_deploy(deploy_type=self.deploy_type)


DeployUtilities = DefaultDeployUtilities


def deploy(deploy_type=utilities.get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')):
    DeployUtilities(deploy_type=deploy_type).start()
