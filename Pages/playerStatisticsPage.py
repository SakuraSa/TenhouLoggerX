#!/usr/bin/env python
# coding=utf-8

"""
Pages.playerStatisticsPage
"""

__author__ = 'Rnd495'

from Pages.APIPage import get_player_statistics
from UI.module.highCharts import high_charts_polar_statistics
from UI.Manager import mapping
from UI.Page import PageBase

import tornado.web
import tornado.gen


@mapping(r'/player/statistics')
class PlayerStatisticsPage(PageBase):
    """
    PlayerStatisticsPage
    """

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        name = self.get_argument('name')
        results = yield get_player_statistics(player_name=name)
        options = None
        if results['ok']:
            options = high_charts_polar_statistics(results['data'], name)
        self.render('player/statistics.html', results=results, options=options, name=name)
