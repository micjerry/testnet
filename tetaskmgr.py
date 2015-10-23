import logging

import tetask


_logger = logging.getLogger(__name__)

class TetaskMgr(object):
    initialized = False
    index = 0
    CONN_NUM = 10
    start_port = 12356
    task_pools = []

    @classmethod
    def initial(cls):
        _logger.info("begin create task pools")
        cls.initialized = True
        for i in range(cls.CONN_NUM):
            task_is = tetask.Tetask(cls.start_port + i, 60)
            cls.task_pools.append(task_is)

    @classmethod
    def finalize(cls):
        _logger.info("close all the tasks")
        list(map(lambda x: x.stop(), cls.task_pools))

    @classmethod
    def check(cls):
        _logger.info("check all the tasks")
        #for item in cls.task_pools:
        #    item.checkexpire()
        list(map(lambda x: x.checkexpire(), cls.task_pools))

    @classmethod
    def starttask(cls, taskid):
        _logger.info("start new task %s" % taskid)
        if not cls.initialized:
            print("begin initial")
            cls.initial()

        for task_is in cls.task_pools:
            if not task_is.gettaskid():
                task_is.start(taskid)
                return task_is.getport()

    @classmethod
    def stoptask(cls, taskid):
        for task_is in cls.task_pools:
            if taskid == task_is.gettaskid():
                task_is.stop()
