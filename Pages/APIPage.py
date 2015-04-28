#!/usr/bin/env python
# coding=utf-8

"""
Pages.APIPage
"""

__author__ = 'Rnd495'

import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.httputil

from UI.Manager import mapping
from UI.Page import PageBase
from core.tenhou.log import Log
from core.models import get_new_session, User


@mapping(r'/api/get_username_availability')
class APIGetUsernameAvailability(PageBase):
    """
    APIGetUsernameAvailability
    """
    def get(self):
        username = self.get_argument("username")
        session = get_new_session()
        availability = not bool(session.query(User).filter(User.name == username).count())
        session.close()
        self.write({'ok': True, 'availability': availability})


@tornado.gen.coroutine
def get_ref_status(ref, user_agent='python-requests/2.5.1 CPython/2.7.6 Windows/7'):
    uploaded = Log.check_exists(ref)
    if not uploaded:
        client = tornado.httpclient.AsyncHTTPClient()
        url = 'http://tenhou.net/5/mjlog2json.cgi?%s' % ref
        headers = {
            'User-Agent': user_agent,
            'Host': 'tenhou.net',
            'Referer': url}
        response = yield client.fetch(url, headers=headers, request_timeout=20)
        if not response:
            raise tornado.gen.Return({'ok': True, 'status': 'connection error', 'already': 'false'})
        elif response.body.strip() == 'INVALID PATH':
            raise tornado.gen.Return({'ok': True, 'status': 'illegal ref', 'already': 'false'})
        else:
            with open(Log.get_file_name(ref), 'wb') as file_handle:
                file_handle.write(response.body)
            raise tornado.gen.Return({'ok': True, 'status': 'ok', 'already': 'false'})
    else:
        raise tornado.gen.Return({'ok': True, 'status': 'ok', 'already': 'true'})


@mapping(r'/api/upload_ref')
class APIUploadRef(PageBase):
    """
    APIUploadRef
    """
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        ref = self.get_argument("ref")
        status = yield get_ref_status(ref)
        self.write(status)
        self.finish()