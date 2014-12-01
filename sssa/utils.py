# -*- coding: UTF-8 -*-
import threading
import Queue
import time
import logging

logger = logging.getLogger("utils")


class ServerStatsSystemAgentHelper(threading.Thread):
    def __init__(self, statsd, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.setName(type(self).__name__ + "-" + self.name)
        self.s = statsd
        self.q = queue
        #
        self.postinit()

    def run(self):
        while self.running:
            try:
                self.q.get(True, 10)
                self.pre()
            except:
                pass

    def pre(self):
        pass

    def postinit(self):
        pass
