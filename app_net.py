import os
import sys

sys.path.append('/opt/webapps/libs')

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.options
import logging
import logging.handlers

from mickey.daemon import Daemon
import mickey.commonconf
import mickey.logutil

from handlers.addtask import AddTaskHandler
from handlers.finishtask import FinishTaskHandler

from tetaskmgr import TetaskMgr

from tornado.options import define, options
define("port", default=18290, help="run on the given port", type=int)
define("cmd", default="run", help="Command")
define("conf", default="/etc/mx_apps/app_net/app_net_is1.conf", help="Server config")
define("pidfile", default="/var/run/app_net_is1.pid", help="Pid file")
define("logfile", default="/var/log/app_net_is1", help="Log file")

class Application(tornado.web.Application):
    def __init__(self):
        handlers=[(r"/testnet/add/newtask", AddTaskHandler),
                  (r"/testnet/finish/task", FinishTaskHandler)
                 ]
        tornado.web.Application.__init__(self, handlers, debug=True)

    def checktime(self):
        logging.info("begin to check timeout")
        TetaskMgr.check()
 
class MickeyDamon(Daemon):
    def run(self):
        mickey.logutil.setuplog(options.logfile)
        app = Application()
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port, options.local_server)

        main_loop = tornado.ioloop.IOLoop.instance()
        interval = 1000
        scheduler = tornado.ioloop.PeriodicCallback(app.checktime, interval, io_loop = main_loop)
        scheduler.start()

        main_loop.start()

    def errorcmd(self):
        print("unkown command")


def micmain():
    tornado.options.parse_command_line()
    tornado.options.parse_config_file(options.conf)

    miceydamon = MickeyDamon(options.pidfile)
    handler = {}
    handler["start"] = miceydamon.start
    handler["stop"] = miceydamon.stop
    handler["restart"] = miceydamon.restart
    handler["run"] = miceydamon.run

    return handler.get(options.cmd, miceydamon.errorcmd)()

if __name__ == "__main__":
    micmain()    
