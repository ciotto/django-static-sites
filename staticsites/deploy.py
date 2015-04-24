__author__ = 'Christian Bianciotto'


from genericpath import exists
from os import makedirs
from os.path import join, dirname
from datetime import datetime
from staticsites import utilities
import logging

from inspect import getmembers, isfunction
from django.conf import settings
from django.utils.module_loading import import_module
from django.http import HttpRequest

def deploy(deploy_type=utilities.get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')):
    for appname in settings.INSTALLED_APPS:
        if appname != 'staticsites':
            try:
                views = import_module(appname + '.views')

                for func_name, function in getmembers(views, isfunction):
                    if hasattr(function, 'is_static_view') and function.is_static_view:
                        path = function.path
                        minify = function.minify
                        gzip = function.gzip
                        deploy_path = function.deploy_path
                        deploy_path_date_format = function.deploy_path_date_format

                        path = utilities.get_path(path, func_name, deploy_type)
                        minify = utilities.get_minify(minify, path, deploy_type)
                        gzip = utilities.get_gzip(gzip, deploy_type)
                        deploy_path = utilities.get_deploy_path(deploy_path, deploy_type)
                        deploy_path_date_format = utilities.get_deploy_path_date_format(deploy_path_date_format, deploy_type)


                        if 'deploy_type' in function.func_code.co_varnames:
                            response = function(HttpRequest(), deploy_type)
                        else:
                            response = function(HttpRequest())

                        full_path = join(deploy_path % {
                            'deploy_type': deploy_type,
                            'asctime': datetime.now().strftime(deploy_path_date_format)
                        }, path)

                        dir_path = dirname(full_path)
                        if not exists(dir_path):
                            makedirs(dir_path)

                        file = None
                        try:
                            file = open(full_path, 'w')
                            file.write(response.content)

                            logging.info('Create %s' % full_path)
                        finally:
                            if file:
                                file.close()
            except ImportError:
                logging.info('No views module for app %s' % appname)
