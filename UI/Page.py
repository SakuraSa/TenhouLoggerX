#!/usr/bin/env python
# coding=utf-8

"""
UI.Page
"""

__author__ = 'Rnd495'

import sys
import traceback

import tornado.web
import tornado.escape
from tornado import httputil
from tornado.log import gen_log

import core.models
from core.configs import Configs
from core.models import User

configs = Configs.instance()


class Interruption(Exception):
    """
    Interruption
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

    def render(self, page):
        raise NotImplementedError()


class NoticeAndRedirectInterruption(Interruption):
    """
    NoticeAndRedirectInterruption
    """

    def __init__(self, message, title='Notice', redirect_to=None, countdown=3):
        self.message = message
        self.title = title
        self.countdown = countdown
        self.redirect_to = redirect_to if redirect_to is not None else '$BACK$'

    def render(self, page):
        page.render('noticeAndRedirect.html',
                    message=self.message,
                    title=self.title,
                    countdown=self.countdown,
                    redirect_to=self.redirect_to)


class PageBase(tornado.web.RequestHandler):
    """
    PageBase
    """
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)

    @property
    def db(self):
        return core.models.get_global_session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id", None)
        if user_id:
            return self.db.query(User).filter(User.id == user_id).first()
        else:
            return None

    def get_login_url(self):
        return '/login'

    def data_received(self, chunk):
        return tornado.web.RequestHandler.data_received(self, chunk)

    def write_error(self, status_code, **kwargs):
        error_type, error_instance, trace = kwargs.pop('exc_info')
        if issubclass(error_type, Interruption):
            error_instance.render(self)
        else:
            if configs.show_error_details:
                message = traceback.format_exc()
            else:
                message = None
            self.render('error.html', status_code=status_code, message=message)

    def _handle_request_exception(self, e):
        if not isinstance(e, Interruption):
            return tornado.web.RequestHandler._handle_request_exception(self, e)

        # copy of tornado.web.RequestHandler._handle_request_exception
        # but remove exception report
        if isinstance(e, tornado.web.Finish):
            # Not an error; just finish the request without logging.
            if not self._finished:
                self.finish()
            return

        # this is not an error
        # do not report exception
        # self.log_exception(*sys.exc_info())

        if self._finished:
            # Extra errors after the request has been finished should
            # be logged, but there is no reason to continue to try and
            # send a response.
            return
        if isinstance(e, tornado.web.HTTPError):
            if e.status_code not in tornado.httputil.responses and not e.reason:
                gen_log.error("Bad HTTP status code: %d", e.status_code)
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
                return
        self.send_error(500, exc_info=sys.exc_info())

    def get_referer(self):
        return self.request.headers.get('referer', None)

    def get_int_argument(self, name, default=None):
        text = tornado.web.RequestHandler.get_argument(self, name=name, default=default)
        if text is None:
            raise NoticeAndRedirectInterruption(u'缺少参数"%s"' % name, title=u'参数错误', countdown=-1)
        try:
            return int(text)
        except ValueError:
            raise NoticeAndRedirectInterruption(
                u'参数"%s"为"%s"无法解析为int' % (name, text),
                title=u'参数错误', countdown=-1)


class TablePage(PageBase):
    """
    TablePage
    """

    def get_table_argument(self, iterator, table_name="table"):
        page_size = self.get_int_argument(table_name + "_page_size", 10)
        page_index = self.get_int_argument(table_name + "_page_index", 0)
        return TableInfo(iterator, page_size=page_size, page_index=page_index, table_name=table_name)

    def get_path_with_change_query(self, **kwargs):
        path = self.request.path
        query_args = []
        query_dict = dict(self.request.query_arguments.iteritems())
        for key, value in kwargs.iteritems():
            query_dict[key] = value
        for key, value in query_dict.iteritems():
            if not isinstance(value, list):
                value = [value]
            value = [
                tornado.escape.url_escape(i.encode('utf-8'))
                if isinstance(i, unicode) else tornado.escape.url_escape(str(i))
                for i in value
            ]
            query_args.append("%s=%s" % (key, ",".join(value)))
        query_string = "&".join(query_args)
        if isinstance(query_string, unicode):
            query_string.encode('utf-8')
        return path + "?" + query_string

    def turn(self, page_index, table_name):
        kwargs = {table_name + '_page_index': page_index}
        return self.get_path_with_change_query(**kwargs)


class TableInfo(object):
    """
    TableInfo
    """

    def __init__(self, iterator, page_size=10, page_index=0, page_nav_size=10, table_name='table'):
        self.iterator = iterator
        self.page_size = page_size
        self.page_index = page_index
        self.page_nav_size = page_nav_size
        self.table_name = table_name
        self.item_count = len(self.iterator) if isinstance(self.iterator, list) else self.iterator.count()
        self.page_count = self.item_count / self.page_size + bool(self.item_count % self.page_size)
        self.item_index_from = self.page_size * self.page_index
        self.item_index_to = min(self.item_count - 1, self.item_index_from + self.page_size)
        self.items = self.iterator[self.item_index_from:self.item_index_to + 1]

    def iter_page_index(self):
        if self.page_index < self.page_nav_size / 2:
            start = max(0, self.page_index - self.page_nav_size / 2)
            end = min(self.page_count, start + self.page_nav_size)
        else:
            end = min(self.page_count, self.page_index + self.page_nav_size / 2)
            start = max(0, end - self.page_nav_size)

        return range(start, end)