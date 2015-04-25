__author__ = 'Christian Bianciotto'


from genericpath import exists
from os import makedirs
from os.path import abspath
from datetime import datetime
from staticsites import utilities
import logging
import io

from inspect import getmembers, isfunction
from django.conf import settings
from django.utils.module_loading import import_module
from django.http import HttpRequest


def deploy(deploy_type=utilities.get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')):
    # Create deploy root
    deploy_root = utilities.get_deploy_root(deploy_type)
    deploy_root_date_format = utilities.get_deploy_root_date_format(deploy_type)
    deploy_root = deploy_root % {
        'deploy_type': deploy_type,
        'asctime': datetime.now().strftime(deploy_root_date_format)
    }
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

            utilities.iterate_dir(path, utilities.copy_file, None, storage)

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

                        file = None
                        try:
                            file = io.BytesIO(response.content)
                            storage.save(path, file)

                            logging.info('Create %s' % path)
                        finally:
                            if file:
                                file.close()
            except ImportError:
                logging.info('No views module for app %s' % appname)
