#!/usr/bin/env python
# coding=utf-8

"""
UI.module.navbar
"""

__author__ = 'Rnd495'

import tornado.web

from UI.Manager import mapping, page_dict


_init_register_list = []
navbar_list = None


def on_navbar(title=None, priority=0):
    """
    show page link to navbar
    """
    def wrapper(target):
        if not issubclass(target, tornado.web.RequestHandler):
            raise ValueError('ValueError: this function should only apply on tornado.web.RequestHandler')
        _init_register_list.append((target, title, priority))
        return target
    # for on args use: @on_navbar
    if isinstance(title, type) and issubclass(title, tornado.web.RequestHandler):
        # set default title as page class name
        default_target = title
        title = default_target.__name__
        wrapper(default_target)
        return default_target
    return wrapper


def _get_enum_list(pretend=None):
    global _init_register_list, navbar_list
    # check if navbar_dict should update
    if _init_register_list or navbar_list is None:
        navbar_list = navbar_list or list()
        # add new pages
        while _init_register_list:
            target, title, priority = _init_register_list.pop()
            if not hasattr(target, "__url__"):
                # missing "__url__" attr
                raise ValueError('ValueError: "%s" does not has attr "__url__", it seems unregistered.')
            else:
                url = pretend if pretend else target.__url__

            navbar_list.append((target, url, title, priority))
        # sort by priority
        navbar_list.sort(key=lambda v: (v[3], title))

    return navbar_list


@mapping(r'navbar')
class Navbar(tornado.web.UIModule):
    """
    Navbar
    """
    def render(self, pretend=None):
        return self.render_string(r'UI/navbar.html', enum_list=_get_enum_list(pretend=pretend))