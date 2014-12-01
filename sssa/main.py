# -*- coding: UTF-8 -*-
import sys
import logging
import Queue
import time
import ConfigParser
import inspect
import socket

import sssa
# from sssa.statsd import Client
# from sssa.statsd import FakeClient as Client

logger = logging.getLogger("main")


class ServerStatsSystemAgent():
    def __init__(self):
        logger.debug("Starting ServerStatsSystemAgent")
        # load config
        self.metrics = {}
        self.loadConfig()
        # launch client
        self.getClient()
        logger.debug(self.client)
        self.loadHelpers()
        #
        #
        self.queue = Queue.Queue()
        #
        #
        #a = sssa.helpers.system.SystemHelper(self.client, self.queue)
        #a.start()

    def getClient(self):
        if self.cfg.get('main', 'fake') == 'true':
            from sssa.statsd import FakeClient as Client
        else:
            from sssa.statsd import Client
        #
        self.client = Client(self.cfg.get('main', 'host'),
                             self.cfg.get('main', 'port'),
                             self.getPrefix(),
                             )

    def getPrefix(self):
        hostname = self.cfg.get('main', 'hostname')
        if hostname == '____':
            hostname = socket.gethostname().replace('.', '_')
        # sssa.servers.hostname.metric
        prefix = "%s.%s.%s" % (self.cfg.get('main', 'prefix'),
                               self.cfg.get('main', 'group'),
                               hostname,
                               )
        return prefix

    def loadConfig(self):
        logger.debug("Reading %s" % sssa.CONFIG_INI)
        self.cfg = ConfigParser.SafeConfigParser(sssa.CONFIG_DEFAUTLS)
        # logger.debug(self.cfg)
        self.cfg.read(sssa.CONFIG_INI)

    def loadHelpers(self):
        import sssa.helpers
        helpers = sssa.helpers.modules
        for h in helpers:
            # all_functions = inspect.getmembers(sys.modules[h], inspect.isfunction)
            # for f in all_functions:
            #     self.metrics[h + '.' + f[0]] = f[1]
            # #
            all_classes = inspect.getmembers(sys.modules[h], inspect.isclass)
            for f in all_classes:
                if f[0].startswith('__'):
                    continue
                self.metrics[h + '.' + f[0]] = f[1]
            #
        # logger.debug("metrics=%s" % self.metrics.keys())

    def run(self):
        # starts helpers
        for m in self.metrics:
            a = self.metrics[m](self.client, self.queue)
            logger.debug(a)
            a.start()
        #
        while True:
            # end = time.time() + self.cfg.getint('main', 'period')
            end = time.time() + 5
            # logger.debug("Debug message")
            # trigger all helpers
            self.queue.put('foo')

            while time.time() < end:
                # logger.debug("wait")
                time.sleep(0.5)
