#!/usr/bin/env python
# coding=utf-8

"""
watchLogPage
"""

__author__ = 'Rnd495'

import urllib

from UI.Manager import mapping
from UI.Page import PageBase


@mapping(r'/watch/log')
class WatchLogPage(PageBase):
    """
    WatchLogPage
    """

    def get(self):
        ref = self.get_argument("ref")
        params = {'log': ref}
        for i in range(4):
            key = "UN%d" % i
            value = self.get_argument(key, None)
            if value is not None:
                params[key] = value
            else:
                break
        try:
            params['tw'] = int(self.get_argument("tw", None))
        except ValueError:
            pass

        # encode unicode to utf-8
        for key in params:
            value = params[key]
            if isinstance(value, unicode):
                params[key] = value.encode("utf-8")

        tenhou_url = 'http://tenhou.net/5/?' + urllib.urlencode(params)
        self.render('watchLog.html', tenhou_url=tenhou_url)