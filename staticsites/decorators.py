__author__ = 'Christian Bianciotto'


import inspect


def staticview(*args, **kwargs):
    def staticview_decorator(func):
        # Used for find annotated functions
        func.is_static_view = True

        func.path = kwargs.get('path', None)
        if inspect.isfunction(func.path):
            func.path = func.path()

        func.minify = kwargs.get('minify', None)
        func.gzip = kwargs.get('gzip', None)
        func.file_storage = kwargs.get('file_storage', None)
        func.encoding = kwargs.get('encoding', None)


        return func
    if not len(kwargs) and len(args) == 1:
        return staticview_decorator(args[0])
    return staticview_decorator
