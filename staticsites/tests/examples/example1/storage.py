__author__ = 'Christian Bianciotto'


from django.core.files.storage import FileSystemStorage


class ExampleFileSystemStorage(FileSystemStorage):
    """
    Extend standard filesystem storage, override location
    """
    def __init__(self, location=None, *args, **kwargs):
        location = 'deploy/example'

        super(ExampleFileSystemStorage, self).__init__(location, *args, **kwargs)

