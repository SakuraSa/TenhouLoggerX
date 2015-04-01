#!/usr/bin/env python
# coding = utf-8

"""
UI.Page
"""

__author__ = 'Rnd495'

import traceback

import tornado.web
import tornado.gen

import core.models
from core import verification
from core import tasks
from core.models import User, GameLog
from core.configs import Configs
from core.celeryIOLoop import CeleryIOLoop
from UI.Manager import mapping

configs = Configs.instance()
celery = CeleryIOLoop()


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
        self.redirect_to = redirect_to if redirect_to is not None else '/'

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
        self._current_user = None

    @property
    def db(self):
        return core.models.get_global_session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id", None)
        if user_id:
            self._current_user = self.db.query(User).filter(User.id == user_id).first()
        else:
            self._current_user = None
        return self._current_user

    def get_login_url(self):
        return '/login'

    def data_received(self, chunk):
        return tornado.web.RequestHandler.data_received(self, chunk)

    def write_error(self, status_code, **kwargs):
        error_type, error_instance, trace = kwargs.pop('exc_info')
        if issubclass(error_type, Interruption):
            error_instance.render(self)
            return
        if configs.show_error_details:
            message = traceback.format_exc()
        else:
            message = None
        self.render('error.html', status_code=status_code, message=message)

    def _handle_request_exception(self, e):
        if not isinstance(e, Interruption):
            return tornado.web.RequestHandler._handle_request_exception(self, e)

        import sys
        from tornado import httputil
        from tornado.log import gen_log

        if isinstance(e, tornado.web.Finish):
            # Not an error; just finish the request without logging.
            if not self._finished:
                self.finish()
            return
        if self._finished:
            # Extra errors after the request has been finished should
            # be logged, but there is no reason to continue to try and
            # send a response.
            return
        if isinstance(e, tornado.web.HTTPError):
            if e.status_code not in tornado.httputil.responses and not e.reason:
                gen_log.error("Bad HTTP status code: %d", e.status_code)
                self.send_error(500, exc_info=sys.exc_info())
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
        else:
            self.send_error(500, exc_info=sys.exc_info())

    def get_referer(self):
        return self.request.headers.get('referer', None)