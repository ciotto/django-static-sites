__author__ = 'Christian Bianciotto'


KEY_TYPE_APP = 'app'
KEY_TYPE_DEPLOY_TYPE = 'deploy_type'
KEY_TYPE_PATH = 'path'


class BaseDict(dict):
    def __getitem__(self, key):
        """
        This method return a value for the given key. If key is not available, return a value for '' key.
        :param key: This is the Key to be searched in the dictionary.
        :return: A value for the given key or for '' key.
        """
        try:
            return super(BaseDict, self).__getitem__(key)
        except KeyError as e:
            if '' in self:
                return super(BaseDict, self).__getitem__('')
            raise e

    def get(self, app='', deploy_type='', extension='', *args, **kwargs):
        """
        Navigate the dictionary tree; use app key for Apps dict; use deploy_type key for DeployTypes dict; use extension
        key for Extensions dict. This method use TYPES_OF_KEY tuple for bind type and key
        :param app:
        :param deploy_type:
        :param extension:
        :param args:
        :param kwargs:
        :return:
        """
        value = None
        for type_of_key, attr in TYPES_OF_KEY:
            if isinstance(self, type_of_key):
                if attr == KEY_TYPE_APP:
                    key = app
                elif attr == KEY_TYPE_DEPLOY_TYPE:
                    key = deploy_type
                elif attr == KEY_TYPE_PATH:
                    key = extension
                else:
                    raise KeyError('Invalid attribute %s' % attr)

                if key is not None:
                    value = self[key]
                else:
                    raise KeyError('Missing %s key' % attr)

                break

        if isinstance(value, BaseDict):
            value = value.get(app, deploy_type, extension, *args, **kwargs)

        return value


class Apps(BaseDict):
    """
    Use this dictionary for discriminate config by Django app name
    """
    pass


class DeployTypes(BaseDict):
    """
    Use this dictionary for discriminate config by deploy_type
    """
    pass


class Extensions(BaseDict):
    """
    Use this dictionary for discriminate config by file extension
    """
    pass


# Use for bind type and key
TYPES_OF_KEY = (
    (Apps, KEY_TYPE_APP),
    (DeployTypes, KEY_TYPE_DEPLOY_TYPE),
    (Extensions, KEY_TYPE_PATH),
)
