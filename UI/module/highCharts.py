#!/usr/bin/env python
# coding=utf-8

"""
highCharts
"""

__author__ = 'Rnd495'

import re
import json

import tornado.web

from UI.Manager import mapping
from core.tenhou.log import Log
from core.configs import Configs


configs = Configs.instance()
DATE_REGEX = re.compile(r'["\']\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?["\']')


@mapping(r'highCharts')
class HighCharts(tornado.web.UIModule):
    """
    HighCharts
    """

    def __init__(self, handler):
        tornado.web.UIModule.__init__(self, handler)
        self.embedded_javascript_text = None

    def render(self, options):
        return self.chart_render_string(options=options)

    def javascript_files(self):
        return [configs.high_charts_js_file]

    def embedded_javascript(self):
        return self.embedded_javascript_text

    def chart_render_string(self, options):
        chart_name = "chart_%x" % id(self.handler)
        options_json_string = DATE_REGEX.sub('Date.parse(\g<0>)', json.dumps(options))
        self.embedded_javascript_text = """
        $(function() { $('#%s').highcharts(%s); });
        """ % (chart_name, options_json_string)
        return self.render_string(r'UI/highCharts.html', chart_name=chart_name)


def high_charts_simple_lines(title, series, subtitle=None, x_axis=None):
    options = {'title': {'text': title}, 'series': series}
    if subtitle is not None:
        options['subtitle'] = {'text': subtitle}
    if x_axis is None:
        length = max(len(s['data']) for s in series)
        options['x_axis'] = {'categories': [str(i + 1) for i in range(length)]}
    else:
        options['x_axis'] = {'categories': x_axis}
    return options


def high_charts_spline_records_pt(records, name, limit=100):
    dans = {}
    counter = 0
    start_time = end_time = None
    for record in reversed(records):
        if record['lobby'] == '0000':
            counter += 1
            if counter > limit:
                break
            start_time = start_time or record['play_time']
            end_time = record['play_time']
            key = record['rule'][0] + u"麻 " + record['dan']
            dans.setdefault(key, list()).append([record['play_time'], record['pt_now']])
    series = [{'name': key, 'data': value} for key, value in dans.iteritems()]
    options = {
        'chart': {'type': 'spline'},
        'title': {'text': name + u' 近%d盘PT曲线' % limit},
        'subtitle': {'text': start_time + ' - ' + end_time},
        'xAxis': {'type': 'datetime'},
        'yAxis': {'min': 0, 'title': {'text': 'PT'}},
        'series': series
    }
    return options


def high_charts_spline_r(iterator, name, limit=100):
    dans = {}
    counter = 0
    start_time = end_time = None
    for player_log in iterator:
        ref = player_log.ref
        lobby = ref.split('-')[2]
        if lobby == '0000':
            counter += 1
            if counter > limit:
                break
            log = Log(ref=ref)
            start_time = start_time or log.time
            end_time = log.time
            player_index = log.get_player_index(name)
            key = u'三麻' if len(log.names) == 3 else u'四麻'
            key += u" " + log.dans[player_index]
            dans.setdefault(key, []).append([log.time.isoformat(), log.rates[player_index]])
    series = [{'name': key, 'data': value} for key, value in dans.iteritems()]
    time_text = 'None - None'
    if start_time and end_time:
        time_text = start_time.isoformat() + ' - ' + end_time.isoformat()
    options = {
        'chart': {'type': 'spline'},
        'title': {'text': name + u' 近%d盘R值曲线' % limit},
        'subtitle': {'text': time_text},
        'xAxis': {'type': 'datetime'},
        'yAxis': {'title': {'text': 'R值'}},
        'series': series
    }
    return options