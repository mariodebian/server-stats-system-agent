#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from distutils.core import setup


def get_debian_version():
    f = open('debian/changelog', 'r')
    line = f.readline()
    f.close()
    version = line.split()[1].replace('(', '').replace(')', '')
    return version

setup(name='server-stats-system-agent',
      description='Send some server stats to statsd daemon',
      version=get_debian_version(),
      author='Mario Izquierdo',
      author_email='mariodebian@gmail.com',
      url='http://www.thinetic.es',
      license='GPLv2',
      platforms=['linux'],
      keywords=['server', 'statsd', 'graphite'],
      scripts=['usr/sbin/sssa'],
      packages=['sssa', 'sssa.helpers'],
      data_files=[('/etc', ['sssa.conf'])]
      )
