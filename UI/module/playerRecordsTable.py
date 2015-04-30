#!/usr/bin/env python
# coding=utf-8

"""
playerRecordsTable
"""

__author__ = 'Rnd495'

import tornado.web

from UI.Manager import mapping


titles = [u'个室', u'用时', u'日期', u'规则', u'顺位', u'段位', u'pt', u'东起', u'南起', u'西起', u'北起', u'操作']


@mapping(r'player_records_table')
class PlayerRecordsTable(tornado.web.UIModule):
    """
    PlayerRecordsTable
    """

    def render(self, table, name):
        return self.render_string(
            r'UI/playerRecordsTable.html',
            table=table,
            name=name,
            titles=titles)