__author__ = 'Christian Bianciotto'


from staticsites.minify import xml
from inspect import isfunction
from staticsites import conf
from os.path import splitext
from django.conf import settings


def get(dictionary, key, default=None):
    '''
    Get key value from dict, if key not exist return value for empty string key
    :param dictionary: the dictionary
    :param key: the key
    :param default:
    :return: key value from dict, if key not exist return value for empty string key
    '''
    if key in dictionary:
        return dictionary[key]
    elif '' in dictionary:
        return dictionary['']
    elif default:
        return default
    else:
        raise KeyError()


def get_conf(key, deploy_type='', input=None):
    '''
    Get configuration from string key
    :param key: the config key
    :param deploy_type: the deploy type
    :return: in order, input[deploy_type] or input[''] settings.STATICSITE_DEFAULTS[deploy_type][key.lower()] or
            settings.STATICSITE_DEFAULTS[''][key.lower()] or settings.key or conf.key or input
    '''
    if input and isinstance(input, dict):
        return get(input, deploy_type)
    # Use == for exclude empty array and False
    elif input == None:
        if hasattr(settings, 'STATICSITE_DEFAULTS'):
            if deploy_type in settings.STATICSITE_DEFAULTS and key.lower() in settings.STATICSITE_DEFAULTS[deploy_type]:
                return settings.STATICSITE_DEFAULTS[deploy_type][key.lower()]
            elif '' in settings.STATICSITE_DEFAULTS and key.lower() in settings.STATICSITE_DEFAULTS['']:
                return settings.STATICSITE_DEFAULTS[''][key.lower()]

        if hasattr(settings, key):
            value = getattr(settings, key)
            if isinstance(value, dict):
                return get(value, deploy_type)
            return value

        value = getattr(conf, key)
        if isinstance(value, dict):
            return get(value, deploy_type)
        return value

    return input


def get_minify_function(minify, path):
    '''
    Return minify function from path or None
    :param path: The path
    :return: The minify function from path or None
    '''
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
    '''
    Check if path has extension included in extensions
    :param path: The path
    :param extensions: The estensions array
    :return: True if path extension is included in extensions array
    '''
    if not path:
        raise ValueError('path must be not None or empty')
    # Use == for exclude empty array
    if extensions == None:
        raise ValueError('extensions must be not None')

    file_name, file_extension = splitext(path)

    if file_extension.lower() in extensions:
        return True

    return False


def is_xml(path):
    '''
    Check if path has extension included in STATICSITE_XML_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_XML_EXTENSIONS
    '''
    return has_extension(path, get_conf('STATICSITE_XML_EXTENSIONS'))


def is_html(path):
    '''
    Check if path has extension included in STATICSITE_HTML_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_HTML_EXTENSIONS
    '''
    return has_extension(path, get_conf('STATICSITE_HTML_EXTENSIONS'))


def is_css(path):
    '''
    Check if path has extension included in STATICSITE_CSS_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_CSS_EXTENSIONS
    '''
    return has_extension(path, get_conf('STATICSITE_CSS_EXTENSIONS'))


def is_js(path):
    '''
    Check if path has extension included in STATICSITE_JS_EXTENSIONS
    :param path: The path
    :return: True if path extension is included in STATICSITE_JS_EXTENSIONS
    '''
    return has_extension(path, get_conf('STATICSITE_JS_EXTENSIONS'))


def get_path(path, func_name, deploy_type):
    '''
    Return the correct file path from input data and configuration
    :param path: The input path or dict
    :param func_name: The view function name
    :param deploy_type: The deploy type
    :return: in order, path[deploy_type] or path[''] or func_name as path or path
    '''
    if path:
        if isinstance(path, dict):
            return get(path, deploy_type)
    else:
        path = func_name.replace('__', '/') + '.html'

    return path


def get_minify(minify, path, deploy_type):
    '''
    Return True or minify function if file can be minified
    :param minify: The input value or dict or minify function
    :param path: The path
    :param deploy_type: The deploy type
    :return: in order, minify function, minify[deploy_type] or minify[''] or get_conf('STATICSITE_MINIFY_') for correct
        extension
    '''
    if minify and isfunction(minify):
        return minify
    else:
    # elif get_minify_function(minify, path):   # log warning when minify
        if isinstance(minify, dict):
            return get(minify, deploy_type)
        # Use == for exclude empty array
        elif minify == None:
            if is_xml(path):
                minify = get_conf('STATICSITE_MINIFY_XML', deploy_type)
            elif is_css(path):
                minify = get_conf('STATICSITE_MINIFY_CSS', deploy_type)
            elif is_js(path):
                minify = get_conf('STATICSITE_MINIFY_JS', deploy_type)
            else:
                minify = False

        return minify

    # return False


def get_gzip(gzip, deploy_type):
    '''
    Return the correct gzip value from input data and configuration
    :param gzip: The input gzip value or dict
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_GZIP', deploy_type, gzip)
    '''
    return get_conf('STATICSITE_GZIP', deploy_type, gzip)


def get_deploy_path(deploy_path, deploy_type):
    '''
    Return the correct deploy_path from input data and configuration
    :param gzip: The input deploy_path or dict
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_DEPLOY_PATH', deploy_type, gzip)
    '''
    return get_conf('STATICSITE_DEPLOY_PATH', deploy_type, deploy_path)


def get_deploy_path_date_format(deploy_path_date_format, deploy_type):
    '''
    Return the correct deploy_path_date_formatp from input data and configuration
    :param gzip: The input deploy_path_date_formatp or dict
    :param deploy_type: The deploy type
    :return: get_conf('STATICSITE_DEPLOY_PATH_DATE_FORMAT', deploy_type, gzip)
    '''
    return get_conf('STATICSITE_DEPLOY_PATH_DATE_FORMAT', deploy_type, deploy_path_date_format)


def get_default_deploy_type():
    '''
    Return the correct default_deploy_type from configuration
    :return: get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')
    '''
    return get_conf('STATICSITE_DEFAULT_DEPLOY_TYPE')
