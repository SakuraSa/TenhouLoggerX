#!/usr/bin/env python
# coding=utf-8

"""
playerLogTable
"""

__author__ = 'Rnd495'

import tornado.web

from UI.Manager import mapping


titles = [u'索引', u'玩家', u'时间']


def extractor(item):
    return item.ref, item.name, item.time.strftime(u'%Y/%m/%d %H')


@mapping(r'player_log_table')
class PlayerLogTable(tornado.web.UIModule):
    """
    PlayerLogTable
    """

    def render(self, iterator, offset=0, limit=10, table_class='table'):
        return self.render_string(
            r'UI/table.html',
            iterator=iterator,
            titles=titles,
            extractor=extractor,
            offset=offset,
            limit=limit,
            table_class=table_class)