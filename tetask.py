import os
import subprocess
import logging

#_start_tcpcmd = "/usr/bin/nohup iperf -su -p%s -i 1 -fm &"
_get_udppid = "ps -ef | grep 'iperf -su -p%s' | grep -v grep | awk '{print $2}'"
_get_tcppid = "ps -ef | grep 'iperf -s -p%s' | grep -v grep | awk '{print $2}'"

_stop_cmd = "kill -9 %s"

class Tetask(object):
    def __init__(self, port, expire):
        self.port  = port
        self.expire = expire
        self.working_time = 0
        self.taskid = None

    def start(self, taskid):
        logging.debug("start task %s", taskid)
        self.working_time = 0
        self.taskid = taskid
        port_para = "-p%s" % self.port
        udp_cmd = ["/usr/bin/iperf", "-su", port_para, "-fm"]
        subprocess.Popen(udp_cmd, stdout=subprocess.DEVNULL)
        tcp_cmd = ["/usr/bin/iperf", "-s", port_para, "-fm"]
        subprocess.Popen(tcp_cmd, stdout=subprocess.DEVNULL)
        

    def stop(self):
        logging.debug("stop task %s" % self.taskid)
        udp_pid = os.popen(_get_udppid % self.port).read()
        if udp_pid:
            os.popen(_stop_cmd % udp_pid).read()
        
        tcp_pid = os.popen(_get_tcppid % self.port).read()
        if tcp_pid:
            os.popen(_stop_cmd % tcp_pid).read()

        self.taskid = None

    def checkexpire(self):
        logging.debug("check expire of %s" % self.taskid)
        if not self.taskid:
            return

        self.working_time = self.working_time + 1
        if self.working_time > self.expire:
            self.stop()

    def gettaskid(self):
        return self.taskid

    def getport(self):
        return self.port
