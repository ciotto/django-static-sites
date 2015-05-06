__author__ = 'Christian Bianciotto'


KEY_TYPE_APP = 'app'
KEY_TYPE_DEPLOY_TYPE = 'deploy_type'
KEY_TYPE_PATH = 'path'


class BaseDict(dict):
    def __getitem__(self, key):
        try:
            return super(BaseDict, self).__getitem__(key)
        except KeyError as e:
            if '' in self:
                return super(BaseDict, self).__getitem__('')
            raise e

    def get(self, app='', deploy_type='', extension='', *args, **kwargs):
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
    pass


class DeployTypes(BaseDict):
    pass


class Extensions(BaseDict):
    pass


TYPES_OF_KEY = (
    (Apps, KEY_TYPE_APP),
    (DeployTypes, KEY_TYPE_DEPLOY_TYPE),
    (Extensions, KEY_TYPE_PATH),
)
