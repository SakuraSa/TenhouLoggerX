#!/usr/bin/env python
# coding = utf-8

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

    tornado.options.parse_command_line()
    app = create_app()
    app.listen(options.port, options.ip)
    print "starting service on %s:%s" % (options.ip, options.port)
    tornado.ioloop.IOLoop.instance().start()