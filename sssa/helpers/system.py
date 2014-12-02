# -*- coding: UTF-8 -*-
import psutil
import threading
import logging
import time

import sssa.utils

logger = logging.getLogger("helpers.system")


class SystemHelper(sssa.utils.ServerStatsSystemAgentHelper):
    _net1 = None
    _net_time = None
    _parts = []
    _name = 'system'

    def postinit(self):
        self._net1 = psutil.net_io_counters(pernic=True)
        self._net_time = time.time()
        self._parts = [x.mountpoint for x in psutil.disk_partitions()]
        return True

    def loop(self):
        if not 'system.disk' in self.disabled:
            self.disk()
        if not 'system.cpu' in self.disabled:
            self.cpu_times_percent()
        if not 'system.mem' in self.disabled:
            self.memory()
        if not 'system.net' in self.disabled:
            self.network()

    def network(self):
        if self._net1:
            tmp = psutil.net_io_counters(pernic=True)
            tx = 0
            rx = 0
            for iface in tmp:
                if iface in ['lo', 'wlan0']:
                    continue
                if ":" in iface:
                    continue
                # logger.debug("iface=%s" % iface)
                tx = tmp[iface].bytes_sent - self._net1[iface].bytes_sent
                rx = tmp[iface].bytes_recv - self._net1[iface].bytes_recv
                #
                diff = time.time() - self._net_time
                #
                self.s.gauge("net.%s.tx_bytes" % iface, int(tx / diff))
                self.s.gauge("net.%s.rx_bytes" % iface, int(rx / diff))
        #
        #
        #
        self._net1 = psutil.net_io_counters(pernic=True)
        self._net_time = time.time()

    def disk(self):
        disk_usage = psutil.disk_usage('/')
        # self.s.gauge('hdd.root.total', disk_usage.total)
        # self.s.gauge('hdd.root.used', disk_usage.used)
        # self.s.gauge('hdd.root.free', disk_usage.free)
        self.s.gauge('hdd.root.percent', disk_usage.percent)

        if '/var' in self._parts:
            disk_usage = psutil.disk_usage('/var')
            # self.s.gauge('hdd.var.total', disk_usage.total)
            # self.s.gauge('hdd.var.used', disk_usage.used)
            # self.s.gauge('hdd.var.free', disk_usage.free)
            self.s.gauge('hdd.var.percent', disk_usage.percent)

        if '/home' in self._parts:
            disk_usage = psutil.disk_usage('/home')
            # self.s.gauge('hdd.home.total', disk_usage.total)
            # self.s.gauge('hdd.home.used', disk_usage.used)
            # self.s.gauge('hdd.home.free', disk_usage.free)
            self.s.gauge('hdd.home.percent', disk_usage.percent)

    # def cpu_times(c):
    #     cpu_times = psutil.cpu_times()
    #     c.gauge('system_wide.times.user', cpu_times.user)
    #     c.gauge('system_wide.times.nice', cpu_times.nice)
    #     c.gauge('system_wide.times.system', cpu_times.system)
    #     c.gauge('system_wide.times.idle', cpu_times.idle)
    #     c.gauge('system_wide.times.iowait', cpu_times.iowait)
    #     c.gauge('system_wide.times.irq', cpu_times.irq)
    #     c.gauge('system_wide.times.softirq', cpu_times.softirq)
    #     c.gauge('system_wide.times.steal', cpu_times.steal)
    #     c.gauge('system_wide.times.guest', cpu_times.guest)
    #     c.gauge('system_wide.times.guest_nice', cpu_times.guest_nice)

    def cpu_times_percent(self):
        value = psutil.cpu_percent(interval=1)
        self.s.gauge('cpu.percent', value)

        cpu_times_percent = psutil.cpu_times_percent(interval=1)
        self.s.gauge('cpu.user', cpu_times_percent.user)
        self.s.gauge('cpu.nice', cpu_times_percent.nice)
        self.s.gauge('cpu.system', cpu_times_percent.system)
        # self.s.gauge('cpu.idle', cpu_times_percent.idle)
        # self.s.gauge('cpu.iowait', cpu_times_percent.iowait)
        # self.s.gauge('cpu.irq', cpu_times_percent.irq)
        # self.s.gauge('cpu.softirq', cpu_times_percent.softirq)
        # self.s.gauge('cpu.steal', cpu_times_percent.steal)
        # self.s.gauge('cpu.guest', cpu_times_percent.guest)
        # self.s.gauge('cpu.guest_nice', cpu_times_percent.guest_nice)

    def memory(self):
        swap = psutil.swap_memory()
        self.s.gauge('swap.total', swap.total)
        # self.s.gauge('swap.used', swap.used)
        # self.s.gauge('swap.free', swap.free)
        self.s.gauge('swap.percent', swap.percent)

        virtual = psutil.virtual_memory()
        self.s.gauge('mem.total', virtual.total)
        self.s.gauge('mem.available', virtual.available)
        # self.s.gauge('mem.used', virtual.used)
        # self.s.gauge('mem.free', virtual.free)
        self.s.gauge('mem.percent', virtual.percent)
        # self.s.gauge('mem.active', virtual.active)
        # self.s.gauge('mem.inactive', virtual.inactive)
        # self.s.gauge('mem.buffers', virtual.buffers)
        # self.s.gauge('mem.cached', virtual.cached)
