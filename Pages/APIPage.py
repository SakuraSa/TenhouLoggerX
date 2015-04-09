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


@mapping(r'/api/upload_ref')
class APIUploadRef(PageBase):
    """
    APIUploadRef
    """
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        ref = self.get_argument("ref")
        uploaded = Log.check_exists(ref)
        if not uploaded:
            client = tornado.httpclient.AsyncHTTPClient()
            url = 'http://tenhou.net/5/mjlog2json.cgi?%s' % ref
            headers = {
                'User-Agent': self.request.headers.get('User-Agent', 'python-requests/2.5.1 CPython/2.7.6 Windows/7'),
                'Host': 'tenhou.net',
                'Referer': url}
            response = yield tornado.gen.Task(client.fetch, url, headers=headers, request_timeout=20)
            if not response:
                self.write({'ok': True, 'status': 'connection error'})
            if response.body.strip() == 'INVALID PATH':
                self.write({'ok': True, 'status': 'illegal ref'})
            else:
                with open(Log.get_file_name(ref), 'wb') as file_handle:
                    file_handle.write(response.body)
                self.write({'ok': True, 'status': 'ok'})
        else:
            self.write({'ok': True, 'status': 'ok'})
        self.finish()