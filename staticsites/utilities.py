import fnmatch

__author__ = 'Christian Bianciotto'


import pickle
from StringIO import StringIO
from conf_dict import BaseDict

import gzip
import re
from os.path import isfile
from os import listdir
from datetime import datetime

from os.path import splitext, join
from django.conf import settings


# Dump / load storage

def dump_storage(storage):
    """
    Return a string by given storage
    :param storage: The storage
    :return: String dump of given storage
    """
    file = StringIO()
    pickle.dump(storage, file)

    return file.getvalue()

def load_storage(string):
    """
    Return storage by dump string
    :param string: The dump string
    :return: Return storage
    """
    file = StringIO(string)

    return pickle.load(file)


# Check extensions

def has_extension(path, extensions):
    """
    Check if path has extension included in extensions
    :param path: The path
    :param extensions: The estensions array
    :return: True if path extension is included in extensions array
    """
    if not path:
        raise ValueError('path must be not None or empty')
    if extensions is None:
        raise ValueError('extensions must be not None')

    file_name, file_extension = splitext(path)

    if file_extension.lower() in extensions:
        return True

    return False

def is_xml(app, deploy_type, path):
    """
    Check if path has extension included in STATICSITE_XML_EXTENSIONS
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The path
    :return: True if path extension is included in STATICSITE_XML_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_XML_EXTENSIONS', app=app, deploy_type=deploy_type, path=path))


def is_html(app, deploy_type, path):
    """
    Check if path has extension included in STATICSITE_HTML_EXTENSIONS
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The path
    :return: True if path extension is included in STATICSITE_HTML_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_HTML_EXTENSIONS', app=app, deploy_type=deploy_type, path=path))


def is_css(app, deploy_type, path):
    """
    Check if path has extension included in STATICSITE_CSS_EXTENSIONS
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The path
    :return: True if path extension is included in STATICSITE_CSS_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_CSS_EXTENSIONS', app=app, deploy_type=deploy_type, path=path))


def is_js(app, deploy_type, path):
    """
    Check if path has extension included in STATICSITE_JS_EXTENSIONS
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The path
    :return: True if path extension is included in STATICSITE_JS_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_JS_EXTENSIONS', app=app, deploy_type=deploy_type, path=path))


# Get configurations

def get_conf(key, app='', deploy_type='', path='', input=None):
    """
    Get correct configuration value, by string key, from input, settings or default conf
    :param key: The config key
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :param input: The input constant or conf_dict
    :return: The correct value of constant key
    """
    file_extension = ''
    if path:
        file_name, file_extension = splitext(path)
    
    if input and isinstance(input, BaseDict):
        return input.get(app=app, deploy_type=deploy_type, extension=file_extension)
    # Use == for exclude empty array and False
    elif input is None:
        if hasattr(settings, key):
            value = getattr(settings, key)
            if isinstance(value, BaseDict):
                return value.get(app=app, deploy_type=deploy_type, extension=file_extension)
            return value

        from staticsites import conf
        value = getattr(conf, key)
        if isinstance(value, BaseDict):
            try:
                return value.get(app=app, deploy_type=deploy_type, extension=file_extension)
            except KeyError:
                pass
        return value

    return input


def get_default_deploy_type():
    """
    Return the correct default_deploy_type from configuration
    :return: get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')
    """
    return get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')


def get_path(func_name=None, app=None, deploy_type=None, path=None):
    """
    Return the correct path from configuration or input value
    :param func_name: The view function name
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :param input: The input constant or conf_dict
    :return: The correct path
    """
    if path:
        if isinstance(path, BaseDict):
            return path.get(app=app, deploy_type=deploy_type)
    else:
        path = func_name.replace('__', '/') + '.html'

    return path


def get_minify(minify=None, app=None, deploy_type=None, path=None):
    """
    Return the correct minify function from configuration or input value
    :param minify: The minify input value or conf_dict
    :param key: The config key
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :return: The minify function or None
    """
    return get_conf('STATICSITE_MINIFY', app=app, deploy_type=deploy_type, path=path, input=minify)


def get_gzip(gzip=None, app=None, deploy_type=None, path=None):
    """
    Return the correct gzip value from configuration or input value
    :param gzip: The input gzip value or conf_dict
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :return: True if need gzip
    """
    return get_conf('STATICSITE_GZIP', app=app, deploy_type=deploy_type, path=path, input=gzip)


def get_encoding(encoding=None, app=None, deploy_type=None, path=None):
    """
    Return the correct encoding value from configuration or input value
    :param encoding: The input encoding value or conf_dict
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :return: The correct encoding value
    """
    return get_conf('STATICSITE_ENCODING', app=app, deploy_type=deploy_type, path=path, input=encoding)


def get_file_storage(file_storage=None, app=None, deploy_type=None, path=None):
    """
    Return the correct file_storage type / file_storage tuple from configuration or input value
    :param file_storage: The input file_storage type or conf_dict
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :return: The file_storage type / file_storage tuple
    """
    return get_conf('STATICSITE_DEFAULT_FILE_STORAGE', app=app, deploy_type=deploy_type, path=path, input=file_storage)


def get_storages(file_storage=None, app=None, deploy_type=None, path=None, **kwargs):
    """
    Return the correct storage instance from configuration or input value
    :param file_storage: The input file_storage type or conf_dict
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :param args: args passed to the input file_storage
    :param kwargs: kwargs passed to the input file_storage
    :return: The correct storage instance
    """
    file_storage = get_file_storage(file_storage, app, deploy_type, path)

    if isinstance(file_storage, list):
        file_storages = file_storage
    else:
        file_storages = [file_storage]

    storages = []
    for file_storage in file_storages:
        if isinstance(file_storage, tuple):
            if len(file_storage) == 2:
                if file_storage[1]:
                    kwargs.update(file_storage[1])

                file_storage = file_storage[0]
            else:
                raise AttributeError('FileStorage tuple must contain FileStorage and **kwargs')

        if 'location' in kwargs:
            kwargs['location'] = get_deploy_root(kwargs['location'], app, deploy_type, path)
        else:
            kwargs['location'] = get_deploy_root(None, app, deploy_type, path)

        storages.append(file_storage(**kwargs))

    return storages

def get_deploy_root(deploy_root=None, app=None, deploy_type=None, path=None):
    """
    Return the correct deploy_root from configuration or input value
    :param deploy_root: The deploy root
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :return: The correct deploy_root
    """
    deploy_root = get_conf('STATICSITE_DEPLOY_ROOT', app=app, deploy_type=deploy_type, path=path, input=deploy_root)
    deploy_root_date_format = get_deploy_root_date_format(None, app, deploy_type, path)
    deploy_root = deploy_root % {
        'deploy_type': deploy_type,
        'asctime': datetime.now().strftime(deploy_root_date_format)
    }

    return deploy_root


def get_deploy_root_date_format(deploy_root_date_format=None, app=None, deploy_type=None, path=None):
    """
    Return the correct deploy_path_date_format from configuration or input value
    :param deploy_type: The deploy type
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :param path: The current destination path
    :return: The correct deploy_path_date_format
    """
    return get_conf('STATICSITE_DEPLOY_ROOT_DATE_FORMAT', app=app, deploy_type=deploy_type, path=path, input=deploy_root_date_format)


def get_default_index(app=None, deploy_type=None):
    """
    Return the correct default_index from configuration or input value
    :param app: The current deploying app
    :param deploy_type: The deploy type
    :return: The correct default_index
    """
    return get_conf('STATICSITE_DEFAULT_INDEX', app=app, deploy_type=deploy_type)


# Navigate into path tree

def iterate_dir(path, callback, ignore=None, deploy_type=None, *args, **kwargs):
    """
    Recursive function, iterate file and call the callback function by passing root path, sub_path and extra args/kwargs
    :param path: The root path
    :param callback: The callback function
    :param ignore: The ignore function, return all ignore file in sub_path
    :param args:
    :param kwargs:
    """
    def _iterate_dir(path, sub_path, callback, ignore, *args, **kwargs):
        tmp_dir = join(path, sub_path)

        dirs = []

        files = listdir(tmp_dir)

        ignore_files = []
        if ignore:
            ignore_files = ignore(path, sub_path, files, deploy_type=deploy_type)

        for node in files:
            node_path = join(tmp_dir, node)

            if node not in ignore_files:
                if isfile(node_path):
                    callback(path, join(sub_path, node), *args, **kwargs)
                else:
                    dirs.append(join(sub_path, node))

        # Iterate the directory after all files
        for node in dirs:
            _iterate_dir(path, node, callback, ignore)

    _iterate_dir(path, "", callback, ignore, *args, **kwargs)


# Read file helper

def read_binary(path):
    """
    Helper function, read binary file content
    :param path: The file path
    :return: The file content
    """
    file = None
    try:
        file = open(path, 'rb')

        return file.read()
    finally:
        if file:
            file.close()


def read_file(path):
    """
    Helper function, read file content
    :param path: The file path
    :return: The file content
    """
    file = None
    try:
        file = open(path, 'r')

        return file.read()
    finally:
        if file:
            file.close()


def read_gzip_file(path):
    """
    Helper function, read gzipped file content
    :param path: The file path
    :return: The file content
    """
    file = None
    try:
        file = gzip.open(path, 'r')

        return file.read()
    finally:
        if file:
            file.close()


# AWS Helper

def invalidate_paths(deploy_type, paths, *args, **kwargs):
    """
    Helper function, create an invalidation request for CloudFront distribution
    :param deploy_type: The deploy type
    :param paths: The paths array
    """
    from boto.cloudfront import CloudFrontConnection
    
    # TODO chunking invalidation to prevent error
    distributions = get_conf('AWS_DISTRIBUTION_ID', deploy_type=deploy_type)

    if isinstance(distributions, list):
        distributions = distributions
    else:
        distributions = [distributions]

    for distribution in distributions:
        conn_cf = CloudFrontConnection(get_conf('AWS_ACCESS_KEY_ID',  deploy_type=deploy_type),
                                       get_conf('AWS_SECRET_ACCESS_KEY',  deploy_type=deploy_type))
        conn_cf.create_invalidation_request(distribution, paths)


# Other

def git_match(pattern, path):
    """
    Return True if path match the pattern (git ignore style)
    :param pattern: The pattern
    :param path: The path
    :return: True if path match the pattern, False otherwise
    """
    return re.search(fnmatch.translate(pattern.lower()), path.lower())

def ignore_file(path, deploy_type=None):
    """
    Return a filtered list of ignored files in sub_path.
    :param path: The root path
    :param sub_path: The current sub path
    :param files: Files in current position
    :param deploy_type: The deploy_type
    :return: Ignored files in sub_path
    """
    ignore_files_patterns = get_conf('STATICSITE_IGNORE_FILES', deploy_type=deploy_type)

    ignore = False

    for pattern in ignore_files_patterns:
        if not pattern.startswith('!') and git_match(pattern, path):
            ignore = True
        elif pattern.startswith('!') and git_match(pattern[1:], path):
            ignore = False

    return ignore

def ignore_files(path, sub_path, files, deploy_type=None):
    """
    Return a filtered list of ignored files in sub_path.
    :param path: The root path
    :param sub_path: The current sub path
    :param files: Files in current position
    :param deploy_type: The deploy_type
    :return: Ignored files in sub_path
    """
    ignore = []

    for file in files:
        full_path = join(sub_path, file)

        if ignore_file(full_path, deploy_type=None):
            ignore.append(file)

    return ignore
