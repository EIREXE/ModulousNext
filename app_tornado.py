from SpaceDock.config import _cfg, _cfgi
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from SpaceDock.app import app
from SpaceDock.app import app

if __name__ == '__main__':
    try:
        http_server = HTTPServer(WSGIContainer(app))
        http_server.bind(_cfgi("debug-port"))
        http_server.start(0)
        IOLoop.instance().start()

    except:
        tornado.ioloop.IOLoop.instance().stop()
