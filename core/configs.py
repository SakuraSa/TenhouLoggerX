#!/usr/bin/env python
# coding = utf-8

"""
core.configs
"""

__author__ = 'Rnd495'
__all__ = ['Configs', 'ConfigsError']

import os


# check "config/now.conf"
# if not exists, create by copying "config/default.conf" to "config/now.conf"
ROOT_PATH = os.path.split(os.path.split(__file__)[0])[0]
CONFIG_PATH_NOW = os.path.join(ROOT_PATH, "config/now.conf")
CONFIG_PATH_DEFAULT = os.path.join(ROOT_PATH, "config/default.conf")
CONFIG_NOTNULL = [
    'database_url',
    'init_admin_username',
    'init_admin_password'
]
if not os.path.exists(CONFIG_PATH_NOW):
    # try to copy from default
    import shutil
    shutil.copy(CONFIG_PATH_DEFAULT, CONFIG_PATH_NOW)
    del shutil


class ConfigsError(Exception):
    """
    ConfigsError
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.error_line = kwargs.get('line', None)


class Configs(object):
    """
    Configs
    """
    def __init__(self, config_file_name):
        with open(config_file_name, 'rb') as file_handle:
            for line in file_handle:
                line = line.strip()
                # lines startswith '#' is commit
                if not line or line.startswith('#'):
                    continue
                separator_index = line.find('=')
                if separator_index < 0:
                    raise ConfigsError('ConfigsError: config line syntax error with "%s"' % line)
                name = line[:separator_index].strip()
                value = line[separator_index + 1:].strip()
                # param type parse
                if value.startswith('"') and value.endswith('"') and len(value) >= 2:
                    value = value[1:len(value) - 1].replace("\\\"", "\"")
                    self.__dict__[name] = value
                elif value in ["True", "true", "False", "false"]:
                    if value in ["True", "true"]:
                        self.__dict__[name] = True
                    else:
                        self.__dict__[name] = False
                else:
                    self.__dict__[name] = int(value)
        for name in CONFIG_NOTNULL:
            if not self.__dict__.get(name, None):
                raise ConfigsError('ConfigsError: property "%s" is not set' % name)

    @staticmethod
    def instance():
        if not hasattr(Configs, "_instance"):
            Configs._instance = Configs(CONFIG_PATH_NOW)
        return Configs._instance

if __name__ == '__main__':
    print "NOW_CONFIGS: "
    print "path:", CONFIG_PATH_NOW
    for k, v in Configs.instance().__dict__.iteritems():
        print k, "=", v