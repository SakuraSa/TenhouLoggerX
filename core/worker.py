#!/usr/bin/env python
# coding=utf-8

"""
tasks
"""

__author__ = 'Rnd495'

from multiprocessing import Pool

from tornado import gen


class Worker(object):
    """
    Worker
    """
    _instance = None

    def __init__(self, processes=None):
        self._pool = Pool(processes=processes)

    def future(self, func, *args, **kwargs):
        """
        :rtype: gen.Future
        """
        return gen.Task(self._pool.apply_async, func, args, kwargs)

    @staticmethod
    def instance():
        """
        :rtype: Worker
        """
        if Worker._instance is None:
            Worker._instance = Worker()
        return Worker._instance


def future(func, *args, **kwargs):
    """
    :rtype: gen.Future
    """
    return Worker.instance().future(func, *args, **kwargs)
