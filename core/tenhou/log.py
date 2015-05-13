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
        win_point = point_change if win else 0
        # speed
        first_richi = self.richi_list[player_index]
        if first_richi:
            for richi in self.richi_list:
                if richi is not None and richi[0] < first_richi[0]:
                    first_richi = False
                    break
        win_time = None
        if win:
            win_time = len(self.cards_ins[player_index])
        # int
        dama = win and not self.is_fulu_list[player_index] and not self.richi_list[player_index]
        ends_listening = self.result_description == u'全員聴牌'
        if self.result_description == u'流局' and self.point_changes[player_index] > 0:
            ends_listening = True
        # def
        chong = self.result_description == u'和了' and self.point_changes[player_index] < 0
        fulu_chong = chong and self.is_fulu_list[player_index]
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