#!/usr/bin/env python
# coding=utf-8

"""
Pages.spiderRedirectPage
"""

__author__ = 'Rnd495'

import urllib

from UI.Manager import mapping
from UI.Page import PageBase


@mapping(r'/playerLogs')
class UploadPage(PageBase):
    """
    UploadPage
    """

    def get(self):
        name = self.get_argument('name', default=u'')
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        query = urllib.urlencode({'name': name})
        self.redirect('player/log/list?' + query)