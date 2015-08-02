#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
exceptions

.. module:: exceptions
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""


class LuxinateException(Exception):

    def __init__(self, message, code=9000):
        super(LuxinateException, self).__init__(message)
        self.code = code


class LuxinateImplementationException(LuxinateException):

    def __init__(self, message, code=9001):
        super(LuxinateImplementationException, self).__init__(message, code)


class LuxinateRequirementException(LuxinateException):

    def __init__(self, message, code=9001):
        super(LuxinateRequirementException, self).__init__(message, code)
