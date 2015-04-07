#!/usr/bin/env python
# coding = utf-8

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
        self.json = json.load(os.path.join(configs.tenhou_log_dir, '%s.json' % ref))

    @staticmethod
    def check_exists(ref):
        return os.path.exists(os.path.join(configs.tenhou_log_dir, '%s.json' % ref))

    @staticmethod
    def download(ref):
        url = 'http://tenhou.net/5/mjlog2json.cgi?%s' % ref
        headers = {
            'Host': 'tenhou.net',
            'Reference': url
        }
        with open(os.path.join(configs.tenhou_log_dir, '%s.ref' % ref)) as file_handle:
            file_handle.write(requests.get(url, headers=headers).text)
        return Log(ref)