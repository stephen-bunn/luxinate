#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
AppleScript

.. module:: AppleScript
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-06-10 15:28:29
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

from __future__ import unicode_literals

import os
import abc
import string
import inspect
import subprocess


class AppleScriptException(Exception):

    def __init__(self, message='undefined error occured', code=2001):
        super(AppleScriptException, self).__init__(message)
        self.code = code

    def __str__(self):
        return repr('{} (code : {})'.format(self.message, self.code))


class ParameterException(AppleScriptException):

    def __init__(self, message='incorrect parameter format', code=2002):
        super(ParameterException, self).__init__(message, code)


class DurationExceededExecption(AppleScriptException):

    def __init__(self, message='duration exceeded', code=2003):
        super(DurationExceededExecption, self).__init__(message, code)


def osascript(process):
    as_cmd = ['osascript', '-e']
    (
        as_cmd.append(process)
        if isinstance(process, basestring) else
        as_cmd.extend(process)
    )
    (proc, proc_err,) = subprocess.Popen(
        as_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()
    if not len(proc_err) <= 0:
        proc_err = proc_err.strip().\
            decode('utf-8').replace(u'\u2018', "'").replace(u'\u2019', "'")
        raise AppleScriptException(
            message=' '.join(proc_err.split(':')[-1].split(' ')[1:-1]),
            code=int(proc_err.split(' ')[-1].split('-')[1][:-1])
        )
    return (True if len(proc) <= 0 else proc.strip())


def _validate_param_format(formats, frame):
    params = inspect.getargvalues(frame)[-1]
    assert isinstance(formats, dict) and isinstance(params, dict), \
        'py:function _validate_param_format requires dict for forms and args'
    evaluation = dict([
        (arg, isinstance(value, formats[arg]),)
        for (arg, value,) in params.iteritems()
        if arg in formats.keys()
    ])
    if not all(evaluation.values()):
        for arg in [k for (k, v,) in evaluation.iteritems() if not v]:
            message = (
                'function `{function}` parameter `{arg}` '
                'expected "{expected}", found {found}'
            ).format(
                function=inspect.getframeinfo(frame).function,
                arg=arg,
                expected='" or "'.join([typ.__name__ for typ in formats[arg]]),
                found='<{}> `{}`'.format(
                    type(params[arg]).__name__,
                    params[arg]
                )
            )
            raise ParameterException(message)
    return True


def _applescript_list(lst):
    assert isinstance(lst, list) or isinstance(lst, tuple)
    return '{{"{}"}}'.format('", "'.join(lst))


def activate(application):
    if _validate_param_format(
        {'application': (basestring,)}, inspect.currentframe()
    ):
        return osascript(
            'activate application "{application}"'.format(
                application=application
            )
        )
    return False


def ASCIICharacter(charint):
    if _validate_param_format({'charint': (int,)}, inspect.currentframe()):
        return osascript(
            'ASCII character {charint}'.format(charint=charint)
        )
    return False


def ASCIINumber(char):
    if _validate_param_format({'char': (basestring,)}, inspect.currentframe()):
        return osascript(
            'ASCII number "{char}"'.format(char=char)
        )
    return False


def beep(amount):
    if _validate_param_format({'amount': (int,)}, inspect.currentframe()):
        return osascript('beep {amount}'.format(amount=amount))
    return False


class AbstractAppleScriptDialog(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def available_parameters(self):
        pass

    @abc.abstractproperty
    def script(self):
        pass

    def valid_parameter_types(self):
        assert isinstance(self.required_parameter_types, dict), (
            'py:function valid_parameter_types requires dict of '
            'class attrs with associated tuple of required types'
        )
        return all([
            isinstance(k, v)
            for (k, v,) in self.required_parameter_types.iteritems()
            if hasattr(self, k)
        ])

    @abc.abstractmethod
    def execute(self):
        pass


class ChooseApplication(AbstractAppleScriptDialog):

    def __init__(self, title,)


class Alert(AbstractAppleScriptDialog):
    _valid_alert_types = ['informational', 'warning', 'critical']

    def __init__(
        self,
        title, message='', alert_type='informational',
        buttons=['Ok', 'Cancel'], default_button='Ok', cancel_button='Cancel',
        duration=None
    ):
        [
            setattr(self, k, v) for (k, v,) in
            inspect.getargvalues(inspect.currentframe())[-1].items()
            if k.lower() != 'self'
        ]
        assert self.valid_parameter_types,\
            'some passed parameter is of incorrect type'
        if alert_type.lower() not in self._valid_alert_types:
            alert_type = self._valid_alert_types[0]
        if len(self.buttons) <= 0:
            self.buttons = ['Ok', 'Cancel']
            (self.default_button, self.cancel_button,) = \
                (self.buttons[0], self.buttons[1],)
        elif len(self.buttons) > 3:
            self.buttons = self.buttons[:3]
        if self.default_button not in self.buttons:
            self.default_button = self.buttons[0]
        if self.cancel_button not in self.buttons:
            self.cancel_button = None

    @property
    def available_parameters(self):
        return {
            'title': (basestring,),
            'message': (basestring,),
            'alert_type': (basestring,),
            'buttons': (list, tuple,),
            'default_button': (basestring,),
            'cancel_button': (basestring,),
            'duration': (int, float,),
        }

    @property
    def script(self):
        return (
            'display alert "{title}" {message} as {alert_type} '
            '{buttons} {default_button} {cancel_button} {duration}'
        ).format(
            title=unicode(self.title),
            message=(
                'message "{}"'.format(unicode(self.message))
                if self.message else
                ''
            ),
            alert_type=self.alert_type,
            buttons="buttons {}".format(__applescript_list(self.buttons)),
            default_button=(
                'default button "{}"'.format(self.default_button)
                if self.default_button else
                ''
            ),
            cancel_button=(
                'cancel button "{}"'.format(self.cancel_button)
                if self.cancel_button else
                ''
            ),
            duration=(
                'giving up after {}'.format(float(self.duration))
                if self.duration else
                ''
            )
        )

    def execute(self):
        retn = osascript(self.script).split(',')
        if len(retn) > 1:
            if retn[-1].split(':')[-1] == 'true':
                raise DurationExceededExecption()
        return retn[0].split(':')[-1]
