import json

class BaseSettings(dict):
    def __init__(self, *args):
        super(BaseSettings, self).__init__()

        for arg in args:
            for k, v in arg.items():
                v = BaseSettings(v) if isinstance(v, dict) else v
                self.__setattr__(k, v)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(BaseSettings, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(BaseSettings, self).__delitem__(key)
        del self.__dict__[key]

with open('settings.json', 'r') as f:
    settingsjson = BaseSettings(json.loads(f.read()))
    print(settingsjson)
