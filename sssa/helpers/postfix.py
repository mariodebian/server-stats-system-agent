# -*- coding: UTF-8 -*-
import os
import threading
import logging
import Queue
import re
import time
import pprint

import sssa.utils


MAIL_LOG = './mail.info'
LOG_OFFSET = '/var/run/sssa-postfix.offset'


logger = logging.getLogger("helpers.postfix")


class PostfixHelper(sssa.utils.ServerStatsSystemAgentHelper):
    def parse_line(self, line):
        try:
            # Apply regular expression to each line and extract interesting bits.
            regMatch = self.reg.match(line)

            if regMatch:
                linebits = regMatch.groupdict()
                if (linebits['status'] == 'sent'):
                    self.totalDelay += float(linebits['send_delay'])
                    self.numSent += 1
                elif (linebits['status'] == 'deferred'):
                    self.numDeferred += 1
                elif (linebits['status'] == 'bounced'):
                    self.numBounced += 1

        except Exception as e:
            raise logger.error("regmatch or contents failed with %s" % e)

    def get_state(self, duration=30):
        self.duration = float(duration)
        totalTxns = self.numSent + self.numBounced + self.numDeferred
        pctDeferred = 100
        pctSent = 100
        pctBounced = 100
        avgDelay = 0
        mailTxnsSec = 0
        mailSentSec = 0

        # mind divide by zero situations
        if (totalTxns > 0):
            pctDeferred = (float(self.numDeferred) / totalTxns) * 100
            pctSent = (float(self.numSent) / totalTxns) * 100
            pctBounced = (float(self.numBounced) / totalTxns) * 100

        if (self.numSent > 0):
            avgDelay = self.totalDelay / self.numSent

        if (self.duration > 0):
            mailTxnsSec = totalTxns / self.duration
            mailSentSec = self.numSent / self.duration

        # Return a list of metrics objects
        return {"num_sent": self.numSent,
                "percent_sent": pctSent,
                "num_deferred": self.numDeferred,
                "percent_deferred": pctDeferred,
                "num_bounced": self.numBounced,
                "percent_bounced": pctBounced,
                "mail_tx_sec": mailTxnsSec,
                "mail_sent_sec": mailSentSec,
                # "avg_delay": avgDelay,
                "duration": duration,
                }

    def resetCounters(self):
        self.numSent = 0
        self.numDeferred = 0
        self.numBounced = 0
        self.totalDelay = 0
        self.numRbl = 0
        self.last = time.time()

    def postinit(self):
        if not os.path.isfile(MAIL_LOG):
            logger.warning('no mail.info')
            return False
        #
        self.first = True
        self.reg = re.compile('.*delay=(?P<send_delay>[^,]+),.*status=(?P<status>(sent|deferred|bounced))')
        self.resetCounters()

        self.lines = Queue.Queue(2000)
        self._log = sssa.utils.LogHelper(MAIL_LOG, LOG_OFFSET)
        self._log.lines = self.lines
        self._log.start()
        #
        return True

    def callback(self, line):
        logger.debug(line)

    def loop(self):
        # logger.debug('postfix')
        while not self.lines.empty():
            line = self.lines.get()
            self.parse_line(line)

        data = self.get_state(time.time() - self.last)
        self.resetCounters()

        # logger.debug('postfix read Queue done')

        if self.first:
            # logger.debug(pprint.pformat(data))
            logger.debug('postfix discard first data')
            self.first = False
            return

        # logger.debug('postfix no first')
        self.s.update_stats("postfix.num_sent", data['num_sent'])
        self.s.update_stats("postfix.num_deferred", data['num_deferred'])
        self.s.update_stats("postfix.num_bounced", data['num_bounced'])

        self.s.gauge("postfix.percent_sent", data['percent_sent'])
        self.s.gauge("postfix.percent_deferred", data['percent_deferred'])
        self.s.gauge("postfix.percent_bounced", data['percent_bounced'])

        self.s.gauge("postfix.mail_tx_sec", data['mail_tx_sec'])
        self.s.gauge("postfix.mail_sent_sec", data['mail_sent_sec'])
