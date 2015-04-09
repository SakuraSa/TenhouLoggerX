#!/usr/bin/env python
# coding=utf-8

"""
playerLogListPage
"""

__author__ = 'Rnd495'

from sqlalchemy import desc

from core.models import get_new_session, PlayerLog
from UI.Manager import mapping
from UI.Page import PageBase


@mapping(r'/player/log/list')
class PlayerLogListPage(PageBase):
    """
    PlayerLogListPage
    """
    def get(self):
        name = self.get_argument('name')
        session = get_new_session()
        iterator = session.query(PlayerLog).filter(PlayerLog.name == name).order_by(desc(PlayerLog.time))
        session.close()
        page_size = int(self.get_argument('page_size', default=1000))
        page_offset = int(self.get_argument('page_offset', default=0))
        page_count = iterator.count()
        offset = page_size * page_offset
        limit = page_size
        self.render(
            'log/list.html',
            iterator=iterator,
            offset=offset, limit=limit,
            page_size=page_size, page_offset=page_offset, page_count=page_count)