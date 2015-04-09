#!/usr/bin/env python
# coding=utf-8

"""
core.tenhou.log
"""

__author__ = 'Rnd495'

import os
import json

import requests

from core.configs import Configs

configs = Configs.instance()


class Log(object):
    """
    Log
    """
    def __init__(self, ref):
        with open(Log.get_file_name(ref), 'rb') as file_handle:
            self.json = json.load(file_handle)

    @staticmethod
    def check_exists(ref):
        return os.path.exists(Log.get_file_name(ref))

    @staticmethod
    def download(ref):
        url = 'http://tenhou.net/5/mjlog2json.cgi?%s' % ref
        headers = {
            'Host': 'tenhou.net',
            'Reference': url
        }
        with open(Log.get_file_name(ref), 'wb') as file_handle:
            file_handle.write(requests.get(url, headers=headers).text)
        return Log(ref)

    @staticmethod
    def get_file_name(ref):
        return os.path.join(configs.tenhou_log_dir, '%s.json' % ref)