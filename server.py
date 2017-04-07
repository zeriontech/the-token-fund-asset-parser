#!/usr/bin/python3
import tornado.ioloop
import tornado.web
import bugsnag
import os
from bugsnag.tornado import BugsnagRequestHandler
from update_daily_performance import update_daily_performance

bugsnag.configure(
    api_key="d2aca67391a3a19947667e8bafce72f2",
    project_root=os.getcwd(),
)


class MainHandler(BugsnagRequestHandler):
    def get(self):
        try:
            update_daily_performance()
            self.write('{"result": "OK"}')
        except Exception as e:
            bugsnag.notify(e)
            self.write('{"result": "ERROR"}')


def make_app():
    return tornado.web.Application([
        (r"/update_table", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888, '0.0.0.0')
    tornado.ioloop.IOLoop.current().start()
