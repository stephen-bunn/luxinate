#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
process

.. module:: process
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-06-10 15:28:29
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

import subprocess


def run_subprocess(process):
    (proc, proc_e,) = subprocess.Popen(
        ([process] if isinstance(process, basestring) else process),
        stdout=subprocess.PIPE,
        shell=isinstance(process, basestring)
    ).communicate()
    return proc
