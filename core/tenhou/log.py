#!/usr/bin/env python
# coding=utf-8

"""
core.tenhou.log
"""

__author__ = 'Rnd495'

import os
import json
import datetime
import urllib

from core.configs import Configs

configs = Configs.instance()


class Log(object):
    """
    Log
    """
    def __init__(self, ref):
        with open(Log.get_file_name(ref), 'rb') as file_handle:
            self.json = json.load(file_handle)

        # cache
        self._scores = None
        self._rankings = None

    @property
    def sub_log(self):
        return self.json['log']

    @property
    def ref(self):
        return self.json['ref']

    @property
    def rule(self):
        return self.json['rule']['disp']

    @property
    def dans(self):
        return self.json['dan']

    @property
    def names(self):
        return self.json['name']

    @property
    def scores(self):
        if not self._scores:
            g = iter(self.json['sc'])
            self._scores = zip(g, g)
        return self._scores

    @property
    def time(self):
        return datetime.datetime.strptime(self.ref[:10], '%Y%m%d%H')

    @property
    def points(self):
        return [point[0] for point in self.scores]

    @property
    def pts(self):
        return [point[1] for point in self.scores]

    @property
    def rankings(self):
        if not self._rankings:
            point_sorted = sorted(((point, index) for index, point in enumerate(self.points)), reverse=True)
            self._rankings = [None] * len(point_sorted)
            for ranking, (_, index) in enumerate(point_sorted):
                self._rankings[index] = ranking
        return self._rankings

    @property
    def rates(self):
        return self.json['rate']

    @staticmethod
    def check_exists(ref):
        return os.path.exists(Log.get_file_name(ref))

    @staticmethod
    def get_file_name(ref):
        return os.path.join(configs.tenhou_log_dir, '%s.json' % ref)

    @staticmethod
    def iter_all():
        for root, dirs, files in os.walk(configs.tenhou_log_dir):
            for file_name in files:
                ref = os.path.splitext(file_name)[0]
                yield Log(ref)

    def get_player_index(self, name):
        try:
            return self.names.index(name)
        except ValueError:
            return None

    def get_tenhou_link(self, tw_name=None):
        base = "/watch/log?"
        params = {'ref': self.ref}
        for i, name in enumerate(self.names):
            if isinstance(name, unicode):
                name = name.encode("utf-8")
            params['UN%d' % i] = name
        tw = None
        if tw_name:
            tw = self.get_player_index(tw_name)
        if tw is not None:
            params['tw'] = tw
        return base + urllib.urlencode(params)


class StatisticForSubLog(object):
    """
    StatisticForSubLog
    """

    def __init__(self, sub_log):
        self.sub_log = sub_log

        self._richi_list = None
        self._fulu_list = None

    @property
    def game_size(self):
        return len(self.point_starts)

    @property
    def game_index(self):
        return self.sub_log[0]

    @property
    def dora_pointers_out(self):
        return self.sub_log[2]

    @property
    def dora_pointers_in(self):
        return self.sub_log[3]

    @property
    def start_cards(self):
        return self.sub_log[4:4 + 3 * self.game_size:3]

    @property
    def cards_ins(self):
        return self.sub_log[5:5 + 3 * self.game_size:3]

    @property
    def cards_outs(self):
        return self.sub_log[6:6 + 3 * self.game_size:3]

    @property
    def result_list(self):
        return self.sub_log[16]

    @property
    def is_agari(self):
        return self.result_description == u'和了'

    @property
    def result_description(self):
        return self.result_list[0]

    @property
    def point_starts(self):
        return self.sub_log[1]

    @property
    def point_changes(self):
        return self.result_list[1::2]

    @property
    def richi_list(self):
        if self._richi_list is None:
            self._get_player_details()
        return self._richi_list

    @property
    def is_fulu_list(self):
        if self._fulu_list is None:
            self._get_player_details()
        return self._fulu_list

    def _get_player_details(self):
        self._richi_list = [None] * self.game_size
        self._fulu_list = [False] * self.game_size
        # scan card outs
        for player_index, card_out in enumerate(self.cards_outs):
            for time_index, action in enumerate(card_out):
                if self._richi_list[player_index] is not None:
                    break
                if self._fulu_list[player_index]:
                    break
                if not isinstance(action, int):
                    if action.startswith('r'):
                        self._richi_list[player_index] = (time_index, action)
                    else:
                        self._fulu_list[player_index] = True
        # scan card ins
        for player_index, card_in in enumerate(self.cards_ins):
            for time_index, action in enumerate(card_in):
                if self._richi_list[player_index] is not None:
                    richi_time, richi_action = self._richi_list[player_index]
                    if time_index >= richi_time:
                        break
                if self._fulu_list[player_index]:
                    break
                elif not isinstance(action, int):
                    self._fulu_list[player_index] = True

    def get_result(self, player_index):
        # attack
        point_change = sum(sc[player_index] for sc in self.point_changes)
        win = self.is_agari and point_change > 0
        win_point = point_change if win else None
        # speed
        first_richi = self.richi_list[player_index]
        if first_richi:
            for richi in self.richi_list:
                if richi is not None and richi[0] < first_richi[0]:
                    first_richi = False
                    break
        first_richi = bool(first_richi)
        win_time = None
        if win:
            win_time = len(self.cards_ins[player_index])
        # int
        dama = None
        if win:
            dama = not self.is_fulu_list[player_index] and not self.richi_list[player_index]
        ends_listening = None
        if self.result_description == u'全員聴牌':
            ends_listening = True
        elif self.result_description == u'流局':
            ends_listening = point_change > 0
        # def
        someone_chong = self.result_description == u'和了' and \
                        len(self.point_changes) == 1 and \
                        sum(p < 0 for p in self.point_changes[0]) == 1
        chong = someone_chong and point_change < 0
        fulu_chong = None
        if chong:
            fulu_chong = self.is_fulu_list[player_index]
        # brave
        after_richi = not first_richi and bool(self.richi_list[player_index])
        fulu = self.is_fulu_list[player_index]
        return dict(
            win=win, win_point=win_point,
            first_richi=first_richi, win_time=win_time,
            dama=dama, ends_listening=ends_listening,
            chong=chong, fulu_chong=fulu_chong,
            after_richi=after_richi, fulu=fulu
        )


def get_results(refs, player_name):
    counter = {}
    adder = {}
    game_date_text_set = set()
    for ref in refs:
        log = Log(ref)
        game_date_text_set.add(log.time.strftime("%Y%m%d"))
        player_index = log.get_player_index(player_name)
        if player_index < 0:
            # should not be here
            continue
        for sub_log in log.sub_log:
            statistics = StatisticForSubLog(sub_log)
            results = statistics.get_result(player_index)
            for key, value in results.iteritems():
                if value is not None:
                    counter[key] = counter.get(key, 0) + 1
                    adder[key] = adder.get(key, 0) + value
    results = {}
    for key, value in counter.iteritems():
        results[key] = (adder[key] / float(value)) if value else 0
    max_line_days = now_line_days = 0
    last_date = None
    for date_text in sorted(game_date_text_set):
        now_date = datetime.datetime.strptime(date_text, "%Y%m%d")
        if last_date:
            if int((now_date - last_date).days) <= 1:
                now_line_days += 1
                max_line_days = max(max_line_days, now_line_days)
            else:
                now_line_days = 1
        last_date = now_date
    results['max_line_days'] = max_line_days
    results['now_line_days'] = now_line_days
    return results


if __name__ == '__main__':
    import time
    from sqlalchemy import func, desc
    from core.models import get_new_session, PlayerLog

    session = get_new_session()
    counter = func.count(PlayerLog.name)
    query = session.query(PlayerLog.name).filter((PlayerLog.lobby == '0000') & (PlayerLog.name != 'NoName')) \
        .group_by(PlayerLog.name).having(counter > 100).order_by(desc(counter))
    results = {}
    for name in (row[0] for row in query):
        start_time = time.time()
        query = session.query(PlayerLog.ref).filter((PlayerLog.name == name) & (PlayerLog.lobby == '0000'))
        refs = [row[0] for row in query]
        results[name] = get_results(refs, name)
        size = len(refs)
        time_cost = time.time() - start_time
        hz = size / time_cost
        print '%6d' % size, '%.2fs' % time_cost, '%.2fHz' % hz, name
    session.close()
    data_lists = {}
    for row in results.itervalues():
        for key, value in row.iteritems():
            data_lists.setdefault(key, []).append(value)

    def format_data(d):
        if d < 1:
            return '%6s' % ('%.2f%%' % (d * 100))
        elif abs(d) < 100:
            return '%6s' % ('%.2f' % d)
        else:
            return '%6s' % ('%d' % d)

    print ''
    print '%20s' % 'type', '%6s' % 'avg', '%6s' % 'max', '%6s' % 'min', '%6s' % 'mse'
    for key, data_list in data_lists.iteritems():
        avg = sum(data_list) / float(len(data_list))
        mse = sum((data - avg) ** 2 for data in data_list) ** 0.5
        print '%20s' % key, format_data(avg), format_data(max(data_list)), format_data(min(data_list)), format_data(mse)