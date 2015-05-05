#!/usr/bin/env python
# coding=utf-8

"""
playerLogListPage
"""

__author__ = 'Rnd495'

from sqlalchemy import desc

from core.models import get_new_session, PlayerLog
from UI.Manager import mapping
from UI.Page import TablePage
from UI.module.highCharts import high_charts_spline_r


@mapping(r'/player/log/list')
class PlayerLogListPage(TablePage):
    """
    PlayerLogListPage
    """
    def get(self):
        name = self.get_argument('name')
        session = get_new_session()
        iterator = session.query(PlayerLog).filter(PlayerLog.name == name).order_by(desc(PlayerLog.time))
        session.close()
        options = high_charts_spline_r(iterator, name)
        table = self.get_table_argument(iterator, table_name='table')
        self.render('log/list.html', table=table, name=name, options=options)