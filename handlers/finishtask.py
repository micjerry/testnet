import tornado.web
import tornado.gen
import json
import io
import logging
import datetime
import calendar

import tornado_mysql
from mickey.mysqlcon import get_mysqlcon

from mickey.ptbasehandler import BaseHandler
from tetaskmgr import TetaskMgr

_inserttcp_sql = """
  INSERT INTO tcpreport(taskId, userId, createAt, upb, downb) 
  VALUES ('%s', '%s', '%s', '%s', '%s');
"""

_insertudp_sql = """
  INSERT INTO udpreport(taskId, userId, createAt, bandWidth, direct, jitter, loseRate)
  VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s');
"""

class FinishTaskHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        data = json.loads(self.request.body.decode("utf-8"))
        taskid = data.get("id", "")
        result = data.get("result", "")
        report = data.get("report", [])
        logging.info("fetch device")

        if not taskid or not result:
            self.set_status(403)
            self.finish()
            return        

        #stop task
        TetaskMgr.stoptask(taskid)
        
        #check result
        if result != "ok":
            self.finish()
            return

        #get create time
        current = calendar.timegm((datetime.datetime.utcnow()).utctimetuple())
        d_current = datetime.datetime.utcfromtimestamp(float(current))
        s_current = d_current.strftime('%Y-%m-%d %H:%M:%S')

        #check report
        for item in report:
            if item.get("type", "") == "tcp":
                yield self.savetcp(item, taskid, s_current)
            else:
                yield self.saveudp(item, taskid, s_current)


        self.finish()

    @tornado.gen.coroutine
    def savetcp(self, tcprp, taskid, s_current):
        upb = tcprp.get("upb", "")
        downb = tcprp.get("downb", "")

        conn = yield get_mysqlcon()
        if not conn:
            logging.error("connect to mysql failed")
            return
        try:
            cur = conn.cursor()
            format_sql = _inserttcp_sql % (taskid, '0', s_current, upb, downb)
            yield cur.execute(format_sql)
            cur.close()

            yield conn.commit()
        except Exception as e:
            logging.error("db oper failed {0}".format(e))
        finally:
            conn.close()

    @tornado.gen.coroutine
    def saveudp(self, udprp, taskid, s_current):
        tb = udprp.get("tb", "")
        direct = udprp.get("direct", "").lower()
        jitter = udprp.get("jitter", "")
        lose = udprp.get("lose", "")

        db_direct = "1"
        if direct == "up":
            db_direct = "0" 

        conn = yield get_mysqlcon()
        if not conn:
            logging.error("connect to mysql failed")
            return

        try:
            cur = conn.cursor()
            format_sql = _insertudp_sql % (taskid, '0', s_current, tb, db_direct, jitter, lose)
            yield cur.execute(format_sql)
            cur.close()

            yield conn.commit()
        except Exception as e:
            logging.error("db oper failed {0}".format(e))
        finally:
            conn.close()

