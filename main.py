#!/usr/bin/env python
# coding=utf-8

"""
main.py
"""

__author__ = 'Rnd495'

if __name__ == '__main__':
    import tornado.ioloop
    from tornado.options import options, define
    from UI.Manager import create_app

    define("port", default=80, help="run on the given port", type=int)
    define("ip", default="0.0.0.0", help="binding on the given ip", type=str)
    define("xheaders", default=False, help="get real ip from X-Read-Ip headers", type=bool)

    tornado.options.parse_command_line()
    app = create_app()
    app.listen(port=options.port, address=options.ip, xheaders=options.xheaders)
    print "starting service on http://%s:%s" % (options.ip, options.port)
    tornado.ioloop.IOLoop.instance().start()
