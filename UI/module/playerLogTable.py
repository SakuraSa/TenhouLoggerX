#!/usr/bin/env python
# coding=utf-8

"""
playerLogTable
"""

__author__ = 'Rnd495'

import tornado.web

from UI.Manager import mapping
from core.tenhou.log import Log


titles = [u'顺位', u'得点', u'PT', u'R值', u'东起', u'南起', u'西起', u'北起', u'时间']


@mapping(r'player_log_table')
class PlayerLogTable(tornado.web.UIModule):
    """
    PlayerLogTable
    """

    def render(self, table, name):
        table.items = [Log(item.ref) for item in table.items]
        return self.render_string(
            r'UI/playerLogTable.html',
            table=table,
            name=name,
            titles=titles)