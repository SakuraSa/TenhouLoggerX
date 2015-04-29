#!/usr/bin/env python
# coding=utf-8

"""
Pages.APIPage
"""

__author__ = 'Rnd495'

import re
import urllib
import datetime

import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.httputil

from UI.Manager import mapping
from UI.Page import PageBase
from core.tenhou.log import Log
from core.models import get_new_session, User, Cache


RECORDS_REGEX = re.compile(r"<div id=\"records\">(?P<records>[\S\s]*)</div>")


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
        try:
            response = yield client.fetch(url, headers=headers, request_timeout=20)
        except tornado.httpclient.HTTPError as error:
            raise tornado.gen.Return({'ok': False, 'status': str(error), 'already': 'false'})
        if not response:
            raise tornado.gen.Return({'ok': False, 'status': 'connection error', 'already': 'false'})
        elif response.body.strip() == 'INVALID PATH':
            raise tornado.gen.Return({'ok': False, 'status': 'illegal ref', 'already': 'false'})
        else:
            with open(Log.get_file_name(ref), 'wb') as file_handle:
                file_handle.write(response.body)
            raise tornado.gen.Return({'ok': True, 'status': 'ok', 'already': 'false'})
    else:
        raise tornado.gen.Return({'ok': True, 'status': 'ok', 'already': 'true'})


@mapping(r'/api/upload/ref')
class APIUploadRef(PageBase):
    """
    APIUploadRef
    """
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        ref = self.get_argument("ref", None)
        if ref:
            status = yield get_ref_status(ref)
            self.write(status)
        else:
            self.write({'ok': False, 'status': "Missing param 'ref'"})


@tornado.gen.coroutine
def get_player_records(name, expire_time=datetime.timedelta(days=1)):
    key = 'records:' + name
    records = Cache.get(key, expire_time=expire_time)
    if records is None:
        client = tornado.httpclient.AsyncHTTPClient()
        query = {'name': name.encode('utf-8') if isinstance(name, unicode) else name}
        url = "http://www.arcturus.su/tenhou/ranking/ranking.pl?" + urllib.urlencode(query=query)
        try:
            response = yield client.fetch(url, request_timeout=20)
        except tornado.httpclient.HTTPError as error:
            raise tornado.gen.Return({'ok': False, 'error': str(error)})
        else:
            text = RECORDS_REGEX.search(response.body).group('records')
            if not text:
                raise tornado.gen.Return({'ok': False, 'error': 'can not found records on page'})
            records = '\n'.join(line.strip() for line in text.split("<br>") if line.strip())
            Cache.set(key, records)
    raise tornado.gen.Return({'ok': True, 'records': records})


@mapping(r'/api/get/records')
class APIGetRecords(PageBase):
    """
    APIGetRecords
    """

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        name = self.get_argument("name", None)
        if name:
            records = yield get_player_records(name)
            self.write(records)
        else:
            self.write({'ok': False, 'status': "Missing param 'name'"})