__author__ = 'Christian Bianciotto'


import gzip
from os.path import isfile
from os import listdir
from datetime import datetime

from staticsites.minify import xml
from inspect import isfunction
from staticsites import conf
from os.path import splitext, join
from django.conf import settings
from boto.cloudfront import CloudFrontConnection


def get(dictionary, key, default=None):
    """
    Get key value from dict, if key not exist return value for empty string key
    :param dictionary: the dictionary
    :param key: the key
    :param default:
    :return: key value from dict, if key not exist return value for empty string key
    """
    if key in dictionary:
        return dictionary[key]
    elif '' in dictionary:
        return dictionary['']
    elif default:
        return default
    else:
        raise KeyError()


def get_conf(key, deploy_type='', input=None):
    """
    Get configuration from string key
    :param key: the config key
    :param deploy_type: the deploy type
    :return: in order, input[deploy_type] or input[''] or settings.key or conf.key or input
    """
    if input and isinstance(input, dict):
        return get(input, deploy_type)
    # Use == for exclude empty array and False
    elif input is None:
        if hasattr(settings, key):
            value = getattr(settings, key)
            if isinstance(value, dict):
                return get(value, deploy_type)
            return value

        value = getattr(conf, key)
        if isinstance(value, dict):
            try:
                return get(value, deploy_type)
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


def get_minify_function(minify, path):
    """
    Return minify function from path or None
    :param path: The path
    :return: The minify function from path or None
    """
    if minify and isfunction(minify):
        return minify

    if not path:
        return xml

    file_name, file_extension = splitext(path)

    staticsite_minify_func = get_conf('STATICSITE_MINIFY_FUNC')

    if file_extension in staticsite_minify_func:
        return get_conf('STATICSITE_MINIFY_FUNC')[file_extension]
    return None


def has_extension(path, extensions):
    """
    Check if path has extension included in extensions
    :param path: The path
    :param extensions: The estensions array
    :return: True if path extension is included in extensions array
    """
    if not path:
        raise ValueError('path must be not None or empty')
    # Use == for exclude empty array
    if extensions is None:
        raise ValueError('extensions must be not None')

    file_name, file_extension = splitext(path)

    if file_extension.lower() in extensions:
        return True

    return False


def is_xml(path):
    """
    Check if path has extension included in STATICSITE_XML_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_XML_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_XML_EXTENSIONS'))


def is_html(path):
    """
    Check if path has extension included in STATICSITE_HTML_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_HTML_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_HTML_EXTENSIONS'))


def is_css(path):
    """
    Check if path has extension included in STATICSITE_CSS_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_CSS_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_CSS_EXTENSIONS'))


def is_js(path):
    """
    Check if path has extension included in STATICSITE_JS_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_JS_EXTENSIONS
    """
    return has_extension(path, get_conf('STATICSITE_JS_EXTENSIONS'))


def get_path(path, func_name, deploy_type=get_default_deploy_type()):
    """
    Return the correct file path from input data and configuration
    :param path: The input path or dict
    :param func_name: The view function name
    :param deploy_type: The deploy type
    :return: in order, path[deploy_type] or path[''] or func_name as path or path
    """
    if path:
        if isinstance(path, dict):
            return get(path, deploy_type)
    else:
        path = func_name.replace('__', '/') + '.html'

    return path


def get_minify(minify, path, deploy_type=get_default_deploy_type()):
    """
    Return the correct minify function for file extension or None
    :param minify: The input value or dict or minify function
    :param path: The path
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_MINIFY', deploy_type, minify)[extension]
    """
    minify = get_conf('STATICSITE_MINIFY', deploy_type, minify)

    if isinstance(minify, dict):
        file_name, file_extension = splitext(path)

        return get(minify, file_extension, None)

    return minify


def get_gzip(gzip, deploy_type=get_default_deploy_type()):
    """
    Return the correct gzip value from input data and configuration
    :param gzip: The input gzip value or dict
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_GZIP', deploy_type, gzip)
    """
    return get_conf('STATICSITE_GZIP', deploy_type, gzip)


def get_file_storage(file_storage, deploy_type=get_default_deploy_type()):
    """
    Return the correct file_storage type from input data and configuration
    :param file_storage: The input file_storage type or dict
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_DEFAULT_FILE_STORAGE', deploy_type, file_storage)
    """
    return get_conf('STATICSITE_DEFAULT_FILE_STORAGE', deploy_type, file_storage)


def get_deploy_root(deploy_type=get_default_deploy_type()):
    """
    Return the correct deploy_path from input data and configuration
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_DEPLOY_ROOT', deploy_type)
    """
    deploy_root = get_conf('STATICSITE_DEPLOY_ROOT', deploy_type)
    deploy_root_date_format = get_deploy_root_date_format(deploy_type)
    deploy_root = deploy_root % {
        'deploy_type': deploy_type,
        'asctime': datetime.now().strftime(deploy_root_date_format)
    }

    return deploy_root


def get_deploy_root_date_format(deploy_type=get_default_deploy_type()):
    """
    Return the correct deploy_path_date_formatp from input data and configuration
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_DEPLOY_ROOT_DATE_FORMAT', deploy_type)
    """
    return get_conf('STATICSITE_DEPLOY_ROOT_DATE_FORMAT', deploy_type)


def get_default_index(deploy_type=get_default_deploy_type()):
    """
    Return the correct default_index from input data and configuration
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_DEFAULT_INDEX', deploy_type)
    """
    return get_conf('STATICSITE_DEFAULT_INDEX', deploy_type)


def set_settings(deploy_type=get_default_deploy_type()):
    """
    Set the correct setting.py constants for deploy_type
    :param deploy_type: The deploy type
    """
    staticsite_settings = get_conf('STATICSITE_SETTINGS', deploy_type)

    for key, value in staticsite_settings.iteritems():
        setattr(settings, key, value)


def iterate_dir(path, callback, ignore=None, *args, **kwargs):
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
            ignore_files = ignore(tmp_dir, files)

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


def invalidate_paths(deploy_type, paths, *args, **kwargs):
    """
    Helper function, create an invalidation request for CloudFront distribution
    :param deploy_type: The deploy type
    :param paths: The paths array
    """
    distributions = get_conf('AWS_DISTRIBUTION_ID', deploy_type)

    if isinstance(distributions, list):
        distributions = distributions
    else:
        distributions = [distributions]

    for distribution in distributions:
        conn_cf = CloudFrontConnection(get_conf('AWS_ACCESS_KEY_ID', deploy_type),
                                       get_conf('AWS_SECRET_ACCESS_KEY', deploy_type))
        conn_cf.create_invalidation_request(distribution, paths)
