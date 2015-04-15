#!/usr/bin/env python
# coding=utf-8

"""
core.tenhou.log
"""

__author__ = 'Rnd495'

import os
import json
import datetime

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

        # cache
        self._scores = None
        self._rankings = None

    @property
    def ref(self):
        return self.json['ref']

    @property
    def names(self):
        return self.json['name']

    @property
    def scores(self):
        if not self._scores:
            g = iter(self.json['sc'])
            self._scores = zip(g, g)
        return self._scores

    @property
    def time(self):
        return datetime.datetime.strptime(self.ref[:10], '%Y%m%d%H')

    @property
    def points(self):
        return [p[0] for p in self.scores]

    @property
    def pts(self):
        return [p[1] for p in self.scores]

    @property
    def rankings(self):
        if not self._rankings:
            index_sorted = sorted((-s, i) for i, s in enumerate(self.points))
            self._rankings = [i for _, i in index_sorted]
        return self._rankings

    @property
    def rates(self):
        return self.json['rate']

    @property
    def ref(self):
        return self.json['ref']

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

    @staticmethod
    def iter_all():
        for root, dirs, files in os.walk(configs.tenhou_log_dir):
            for file_name in files:
                ref = os.path.splitext(file_name)[0]
                yield Log(ref)

    def get_player_index(self, name):
        return self.names.index(name)