#!/usr/bin/env python
# coding=utf-8

"""
viewPlayerPage
"""

__author__ = 'Rnd495'

from UI.Manager import mapping
from UI.Page import PageBase


@mapping(r'/player/view')
class PlayerViewPage(PageBase):
    """
    PlayerViewPage
    """

    def get(self):
        name = self.get_argument("name")
        self.render("player/view.html", name=name)