#!/usr/bin/env python
# coding=utf-8

"""
playerRecordsListPage
"""

__author__ = 'Rnd495'

import tornado.web
import tornado.gen

from UI.Manager import mapping
from UI.Page import TablePage, NoticeAndRedirectInterruption
from UI.module.highCharts import high_charts_spline_records_pt
from Pages.APIPage import get_player_records


@mapping(r'/player/record/list')
class PlayerRecordsListPage(TablePage):
    """
    PlayerRecordsListPage
    """

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        name = self.get_argument('name')
        records = yield get_player_records(name=name)
        if not records['ok']:
            raise NoticeAndRedirectInterruption(u'获取列表时发生错误：' + records['error'], title='错误', countdown=60)
        table = self.get_table_argument(records['records'][::-1], table_name='table')
        options = high_charts_spline_records_pt(records=records['records'], name=name)
        self.render('records/list.html', table=table, name=name, options=options)