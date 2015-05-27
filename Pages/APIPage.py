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
from core.tenhou.log import Log, get_results
from core.worker import future
from core.models import get_new_session, User, PlayerLog, Cache


ENCODING_REGEX = re.compile(r"<meta charset=\"(?P<encoding>.+?)\">")
RECORDS_REGEX = re.compile(r"<div id=\"records\">(?P<records>[\S\s]*)</div>")
REF_REGEX = re.compile(r'(\d{10}gm-\w{4}-\d{4,5}-\w{8})')
PT_REGEX = re.compile(r'\(([\+-]\d+\.\d+)\)')
CHANGE_REGEX = re.compile(r'<abbr title=\"(?P<pt_now>\d+)pt( (?P<pt_change>[\+-]\d+))?\">(?P<dan>\S+)</abbr>')


@mapping(r'/api/get_username_availability')
class APIGetUsernameAvailability(PageBase):
    """
    APIGetUsernameAvailability
    """
    def get(self):
        username = self.get_argument("username")
        session = get_new_session()
        availability = session.query(User).filter(User.name == username).count() == 0
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
            session = get_new_session()
            log = Log(ref=ref)
            for name in log.names:
                session.add(
                    PlayerLog(
                        name=name, ref=ref, time=log.time,
                        lobby=log.lobby, rule=log.rule_code, size=log.size
                    )
                )
            session.commit()
            session.close()
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
            response = yield client.fetch(url, request_timeout=30)
        except tornado.httpclient.HTTPError as error:
            raise tornado.gen.Return({'ok': False, 'error': str(error)})
        else:
            body = response.body
            match_encoding = ENCODING_REGEX.search(body)
            encoding = match_encoding.group('encoding') if match_encoding else 'utf-8'
            records_match = RECORDS_REGEX.search(response.body.decode(encoding))
            text = records_match.group('records') if records_match else None
            if not text:
                raise tornado.gen.Return({'ok': False, 'error': 'can not found records on page'})
            lines = (line.strip() for line in text.split("<br>") if line.strip())
            lines = [[part.strip() for part in line.strip().split('|', 8)] for line in lines]
            records = []
            for line in lines:
                ranking = line[0].strip()
                lobby = line[1].lstrip('L')
                time_cost = int(line[2]) if line[2].isdigit() else None
                play_time = datetime.datetime.strptime(' '.join(line[3:5]), '%Y-%m-%d %H:%M')
                rule = line[5].rstrip(u'\uff0d\uff0d')
                ref = None
                if line[6] != '---':
                    match = REF_REGEX.search(line[6])
                    if match:
                        ref = match.group(0)
                pt_now = None
                pt_change = None
                dan = None
                if line[7] != '---':
                    match = CHANGE_REGEX.search(line[7])
                    if match:
                        pt_now = int(match.group('pt_now'))
                        if match.group('pt_change'):
                            pt_change = int(match.group('pt_change'))
                        dan = match.group('dan')
                result = line[8]
                pts = PT_REGEX.findall(result)
                names = [name.strip() for i, name in enumerate(PT_REGEX.split(result)) if i % 2 == 0 and name.strip()]
                records.append({
                    'ranking': ranking,
                    'pt_now': pt_now,
                    'pt_change': pt_change,
                    'dan': dan,
                    'lobby': lobby,
                    'time_cost': time_cost,
                    'play_time': play_time.isoformat(),
                    'rule': rule,
                    'ref': ref,
                    'pts': pts,
                    'names': names
                })
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


@tornado.gen.coroutine
def get_player_statistics(player_name, lobby='0000', limit=300, game_size=4, min_count=30):
    result_dict = {}

    # query refs
    session = get_new_session()
    query = session.query(PlayerLog.ref) \
        .filter((PlayerLog.name == player_name) & (PlayerLog.lobby == lobby) & (PlayerLog.size == game_size)) \
        .order_by(PlayerLog.time)
    # when ref count < min_count, return error
    total_count = query.count()
    if total_count < min_count:
        # write status and error info
        result_dict['ok'] = False
        result_dict['error'] = u'至少需要上传%d盘记录才能进行统计（已上传%d盘）' % (min_count, total_count)
        session.close()
        raise tornado.gen.Return(result_dict)
    refs = [row[0] for row in query[:limit]]
    session.close()

    # create statistics
    statistic_result = yield future(get_results, ref_list=refs, player_name=player_name)

    # write status
    result_dict['ok'] = True
    result_dict['data'] = statistic_result
    raise tornado.gen.Return(result_dict)
