#!/usr/bin/env python
# coding=utf-8

"""
watchLogPage
"""

__author__ = 'Rnd495'

import re
import urllib

import tornado.web
import tornado.gen

from UI.Manager import mapping
from UI.Page import PageBase, NoticeAndRedirectInterruption
from Pages.APIPage import get_ref_status

TENHOU_REG = re.compile(r"^(?P<ref>\d{10}gm-\w{4}-\d{4,5}-\w{8})$")


@mapping(r'/watch/log')
class WatchLogPage(PageBase):
    """
    WatchLogPage
    """

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        ref = self.get_argument("ref", None)
        if ref is None or not TENHOU_REG.match(ref):
            raise NoticeAndRedirectInterruption(u'无效的索引值"%s"' % ref, title=u'参数错误')

        # check log existence
        status = yield get_ref_status(ref)
        if status['status'] != 'ok':
            raise NoticeAndRedirectInterruption(u'无效的索引值"%s",%s' % (ref, status['status']), title=u'参数错误')

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
        self.finish()