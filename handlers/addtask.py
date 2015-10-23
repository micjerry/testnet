import tornado.web
import tornado.gen
import json
import io
import logging
import uuid

from mickey.basehandler import BaseHandler
from tetaskmgr import TetaskMgr

class AddTaskHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        userid = data.get("id", "").lower()
        #logging.info("%s fetch device %s" % (self.p_userid))

        taskid = str(uuid.uuid4()).replace('-', '_')
        available_task = TetaskMgr.starttask(taskid)
        if available_task:
            result = {}
            result["id"] = taskid
            result["port"] = str(available_task)
            result["expire"] = "60"
            self.write(result)
            self.finish()
            return

        self.set_status(408)
        self.finish()
                