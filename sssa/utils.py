# -*- coding: UTF-8 -*-
import os
import threading
import Queue
import time
import logging

logger = logging.getLogger("utils")


class ServerStatsSystemAgentHelper(threading.Thread):
    _name = ''

    def __init__(self, statsd, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.setName(type(self).__name__ + "-" + self.name)
        self.s = statsd
        self.q = queue
        self.cfg = None
        #
        # only run if postinit() return True
        self.running = self.postinit()
        #

    def run(self):
        #
        self.disabled = self.getConfig('disabled').split(',')
        # check if all helper is disabled
        if self._name in self.disabled:
            logger.debug("%s is disabled" % self._name)
            self.running = False
        #
        while self.running:
            try:
                self.q.get(True, 10)
                self.loop()
            except:
                pass

    def loop(self):
        pass

    def postinit(self):
        return True

    def getConfig(self, varname, section='main', default=None):
        # self.cfg.get(section, varname)
        #
        if not self.cfg.has_option(section, varname):
            return default
        #
        return self.cfg.get(section, varname)


from sssa.pygtail import Pygtail


class LogHelper(threading.Thread):
    def __init__(self, logfile, offset):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True
        self.logfile = logfile
        self.offset = offset

    def run(self):
        #
        if os.path.isfile(self.offset):
            os.unlink(self.offset)
        #
        while self.running:
            for line in Pygtail(self.logfile, offset_file=self.offset):
                self.lines.put(line)
            time.sleep(1)
