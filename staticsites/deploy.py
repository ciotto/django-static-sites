__author__ = 'Christian Bianciotto'


from gzip import GzipFile

from os.path import abspath, join, getmtime
from staticsites import utilities
from datetime import datetime
import hashlib
import logging
import StringIO

from inspect import getmembers, isfunction
from django.conf import settings
from django.utils.module_loading import import_module
from django.db.models import Q
from django.http import HttpRequest

from models import DeployOperation, Deploy


class DefaultDeployUtilities:
    def __init__(self, deploy_type, force):
        self.deploy_type = deploy_type
        self.force = force
        self.deploy = None
        self.storage = None

        self.paths = []
        self.deploy_operations = []

    def copy(self, path, sub_path, staticfiles_dir=None, *args, **kwargs):
        full_path = join(path, sub_path)

        file_storage = None
        if staticfiles_dir and len(staticfiles_dir) > 1:
            file_storage = staticfiles_dir[1]

        # TODO get also from staticfiles dir (trasforme tupla to dict?)
        minify = utilities.get_minify(None, None, self.deploy_type, sub_path)
        gzip = utilities.get_gzip(None, None, self.deploy_type, sub_path)
        storages = utilities.get_storages(file_storage, None, self.deploy_type, sub_path, **kwargs)
        encoding = utilities.get_encoding(None, None, self.deploy_type, sub_path)

        gzip_ignore_files = utilities.get_conf('STATICSITE_GZIP_IGNORE_FILES',
                                               deploy_type=self.deploy_type,
                                               path=sub_path)
        minify_ignore_files = utilities.get_conf('STATICSITE_MINIFY_IGNORE_FILES',
                                                 deploy_type=self.deploy_type,
                                                 path=sub_path)

        for self.storage in storages:
            file = None
            try:
                operation_type = 'N'

                if self.storage.exists(sub_path):
                    # Check if need update by checking modification date
                    if self.force or datetime.fromtimestamp(getmtime(full_path)) > self.storage.modified_time(sub_path):
                        self.storage.delete(sub_path)
                        operation_type = 'U'
                    else:
                        operation_type = 'NU'
                        logging.info('File %s not updated' % path)

                if operation_type is not 'NU':
                    if minify or gzip:
                        if minify and sub_path not in minify_ignore_files:
                            content = utilities.read_file(full_path)
                            try:
                                content = minify(content)
                            except Exception as e:
                                logging.warning('Error occurred during minify on file %s: %s' % (full_path, e.message))
                        else:
                            content = utilities.read_binary(full_path)

                        if gzip and sub_path not in gzip_ignore_files:
                            #TODO append .gz extension (config)
                            file = StringIO.StringIO()
                            gzip_file = GzipFile(fileobj=file, mode="w")
                            gzip_file.write(content)
                            gzip_file.close()
                        else:
                            file = StringIO.StringIO(content)
                    else:
                        file = open(full_path, 'rb')
                    self.storage.save(sub_path, file)

                    if operation_type is 'U':
                        logging.info('Update file %s' % sub_path)
                    else:
                        logging.info('Create static file %s' % sub_path)

                dpo = DeployOperation(deploy=self.deploy,
                                      file_type='S',
                                      operation_type=operation_type,
                                      path=sub_path,
                                      storage=utilities.dump_storage(self.storage))
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

        before_deploy = utilities.get_conf('STATICSITE_BEFORE_DEPLOY', deploy_type=self.deploy_type)
        after_deploy = utilities.get_conf('STATICSITE_AFTER_DEPLOY', deploy_type=self.deploy_type)

        if before_deploy:
            before_deploy(deploy_type=self.deploy_type, deploy=self.deploy)

        # Copy static files
        staticfiles_dirs = utilities.get_conf('STATICSITE_STATICFILES_DIRS', self.deploy_type)
        if staticfiles_dirs:
            for staticfiles_dir in staticfiles_dirs:
                path = abspath(staticfiles_dir[0])

                ignore = utilities.get_conf('STATICSITE_IGNORE', deploy_type=self.deploy_type)

                utilities.iterate_dir(path, self.copy, ignore, staticfiles_dir)

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
                            encoding = function.encoding

                            path = utilities.get_path(func_name, appname, self.deploy_type, path)
                            minify = utilities.get_minify(minify, appname, self.deploy_type, path)
                            gzip = utilities.get_gzip(gzip, appname, self.deploy_type, path)
                            encoding = utilities.get_encoding(encoding, appname, self.deploy_type, path)

                            gzip_ignore_files = utilities.get_conf('STATICSITE_GZIP_IGNORE_FILES',
                                                                   deploy_type=self.deploy_type,
                                                                   path=path)
                            minify_ignore_files = utilities.get_conf('STATICSITE_MINIFY_IGNORE_FILES',
                                                                     deploy_type=self.deploy_type,
                                                                     path=path)

                            if 'deploy_type' in function.func_code.co_varnames:
                                response = function(HttpRequest(), self.deploy_type)
                            else:
                                response = function(HttpRequest())

                            content = response.content
                            if minify and path not in minify_ignore_files:
                                try:
                                        content = minify(content, encoding=encoding)
                                except Exception as e:
                                    logging.warning('Error occurred during minify on view %s: %s' % (func_name, e.message))

                            storages = utilities.get_storages(file_storage, None, self.deploy_type, None)

                            for self.storage in storages:

                                new_dpo = DeployOperation(deploy=self.deploy,
                                                          file_type='D',
                                                          operation_type='N',
                                                          path=path,
                                                          hash=hashlib.sha512(content).hexdigest(),
                                                          storage=utilities.dump_storage(self.storage))

                                if self.storage.exists(path):
                                    # Check if need update by checking stored hash
                                    last_dpo = None
                                    if last_dp:
                                        deploy_operations = DeployOperation.objects.filter(path=path, deploy=last_dp)
                                        if deploy_operations:
                                            last_dpo = deploy_operations[0]

                                    if not self.force and last_dpo and last_dpo.hash and new_dpo.hash == last_dpo.hash:
                                        new_dpo.operation_type = 'NU'
                                        logging.info('File %s not updated' % path)
                                    else:
                                        self.storage.delete(path)
                                        new_dpo.operation_type = 'U'

                                if new_dpo.operation_type is not 'NU':
                                    file = None
                                    try:
                                        if gzip and path not in gzip_ignore_files:
                                            #TODO gzip config discriminate extension
                                            #TODO append .gz extension (config)
                                            file = StringIO.StringIO()
                                            gzip_file = GzipFile(fileobj=file, mode="w")
                                            gzip_file.write(content)
                                            gzip_file.close()
                                        else:
                                            file = StringIO.StringIO(content)

                                        self.storage.save(path, file)

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
                storage = utilities.load_storage(path.storage)
                storage.delete(path.path)
                new_dpo = DeployOperation(deploy=self.deploy,
                                          file_type=path.file_type,
                                          operation_type='R',
                                          path=path.path,
                                          hash=path.hash,
                                          storage=path.storage)
                new_dpo.save()
                self.deploy_operations.append(new_dpo)
                if path not in self.paths:
                    self.paths.append(path)

        if after_deploy:
            after_deploy(deploy_type=self.deploy_type, paths=self.paths, deploy=self.deploy)


DeployUtilities = DefaultDeployUtilities


def deploy(deploy_type=utilities.get_default_deploy_type(), force=False):
    DeployUtilities(deploy_type=deploy_type, force=force).start()
