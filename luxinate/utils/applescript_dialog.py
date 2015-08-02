#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
applescript_dialog

.. module:: applescript_dialog
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

from __future__ import unicode_literals

import os
import abc
import inspect
import logging
import subprocess


AUTHOR = 'The Alfred Bundler Team'
DATE = '07-16-15'
VERSION = '1.0'

# XXX: setting the basicConfig of the logger propogates to other logs...
# logging.basicConfig(
#     level=logging.DEBUG,
#     format=('[%(asctime)s] '
#             '[{}:%(lineno)d] '
#             '[%(levelname)s] '
#             '%(message)s').format(os.path.basename(__file__)),
#     datefmt='%H:%M:%S'
# )


class AppleScriptException(Exception):

    def __init__(self, message='undefined exception', code=9000):
        super(AppleScriptException, self).__init__(message)
        self.code = code

    def __str__(self):
        return repr(
            '{message} (code : {code})'.format(
                message=self.message,
                code=self.code
            )
        )


class UserCanceledException(AppleScriptException):
    pass


class DurationExceededException(AppleScriptException):

    def __init__(self, message='dialog gave up', code=9001):
        super(DurationExceededException, self).__init__(message)


class AppleScriptDialog:
    # TODO: Massive commenting/documentation ... ugh

    def __init__(self, debug=False):
        self.debug = debug
        self.log = logging.getLogger(self.__class__.__name__)

    def _osascript(self, script):
        cmd = ['osascript', '-e']
        (
            cmd.append(script)
            if isinstance(script, basestring) else
            cmd.extend(script)
        )
        (proc, proc_e,) = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()
        if proc_e and len(proc_e) > 0:
            proc_e = ''.join([
                i
                for i in proc_e.strip().decode('utf-8')
                if 0 < ord(i) < 127
            ])
            proc_e_msg = ' '.join(proc_e.split(':')[-1].split(' ')[1:-1])
            proc_e_code = int(proc_e.split(' ')[-1].split('-')[-1][:-1])
            if proc_e_code == 128:
                raise UserCanceledException(proc_e_msg, proc_e_code)
            raise AppleScriptException(proc_e_msg, proc_e_code)
        return (proc.strip() if len(proc) > 0 else True)

    def _applescript_list(self, lst):
        return '{{"{}"}}'.format('", "'.join(lst))

    def _applescript_alias(self, path):
        return '(POSIX file "{}" as alias)'.format(path)

    def _format_passed(self, passed):
        return dict([(k.lower(), v,) for (k, v,) in passed.iteritems()])

    def _valid_options(self, passed, custom_options):
        _is_valid = True
        _funct = custom_options['function']
        valid_passed = dict(custom_options['custom_options'].items())

        for passed_key in passed.keys():
            if passed_key in valid_passed.keys():
                if not isinstance(
                    passed[passed_key],
                    valid_passed[passed_key]
                ):
                    if self.debug:
                        self.log.warning((
                            '{funct}, removing ({passed}) invalid type, '
                            'expected ({expected}), got ({got})'
                        ).format(
                            funct=_funct,
                            passed=passed_key,
                            expected=' or '.join(
                                i.__name__ for i in valid_passed[passed_key]
                            ),
                            got=type(passed[passed_key]).__name__
                        ))
                    del passed[passed_key]
            else:
                if self.debug:
                    self.log.warning((
                        '{funct}, removing ({passed}) invalid parameter, '
                        'available are ({available})'
                    ).format(
                        funct=_funct,
                        passed=passed_key,
                        available=', '.join(valid_passed.keys())
                    ))
                del passed[passed_key]

        for required_key in custom_options['required_options']:
            if required_key not in passed.keys():
                if self.debug:
                    self.log.error((
                        '{funct}, missing required parameter ({required})'
                    ).format(funct=_funct, required=required_key))
                _is_valid = False

        return _is_valid

    def _build_passed(self, passed):
        passed_keys = passed.keys()
        available_servers = (
            'Web servers', 'FTP Servers', 'Telnet hosts', 'File servers',
            'News servers', 'Directory services', 'Media servers',
            'Remote applications',
        )
        available_alert_types = ('informational', 'warning', 'critical',)
        available_icons = (0, 'stop', 1, 'note', 2, 'caution',)
        extdict = {
            'title': (
                'with title "{}"'.format(passed['title'])
                if 'title' in passed_keys and len(passed['title']) > 0 else
                None
            ),
            'prompt': (
                'with prompt "{}"'.format(passed['prompt'])
                if 'prompt' in passed_keys and len(passed['prompt']) > 0 else
                None
            ),
            'message': (
                'message "{}"'.format(passed['message'])
                if 'message' in passed_keys and len(passed['message']) > 0 else
                None
            ),
            'subtitle': (
                'subtitle "{}"'.format(passed['subtitle'])
                if 'subtitle' in passed_keys and
                len(passed['subtitle']) > 0 else
                None
            ),
            'multiple_selections_allowed': (
                'multiple selections allowed true'
                if 'multiple_selections_allowed' in passed_keys and
                passed['multiple_selections_allowed'] else
                None
            ),
            'empty_selection_allowed': (
                'empty selection allowed true'
                if 'empty_selection_allowed' in passed_keys and
                passed['empty_selection_allowed'] else
                None
            ),
            'as_': (
                'as {}'.format(passed['as'])
                if 'as' in passed_keys and
                passed['as'] in ('application', 'alias',) else
                None
            ),
            'type': (
                'of type {}'.format(self._applescript_list(passed['type']))
                if 'type' in passed_keys and len(passed['type']) > 0 else
                None
            ),
            'default_name': (
                'default name "{}"'.format(passed['default_name'])
                if 'default_name' in passed_keys and
                len(passed['default_name']) > 0 else
                None
            ),
            'default_location': (
                'default location {}'.format(
                    self._applescript_alias(passed['default_location'])
                )
                if 'default_location' in passed_keys and
                os.path.exists(passed['default_location']) else
                None
            ),
            'default_items': (
                'default items {}'.format(
                    self._applescript_list(passed['default_items'])
                )
                if 'default_items' in passed_keys and
                len(passed['default_items']) > 0 else
                None
            ),
            'invisibles': (
                'invisibles true'
                if 'invisibles' in passed_keys and passed['invisibles'] else
                None
            ),
            'showing_package_contents': (
                'showing package contents true'
                if 'showing_package_contents' in passed_keys and
                passed['showing_package_contents'] else
                None
            ),
            'ok_button_name': (
                'OK button name "{}"'.format(passed['ok_button_name'])
                if 'ok_button_name' in passed_keys and
                len(passed['ok_button_name']) > 0 else
                None
            ),
            'cancel_button_name': (
                'cancel button name "{}"'.format(passed['cancel_button_name'])
                if 'cancel_button_name' in passed_keys and
                len(passed['cancel_button_name']) > 0 else
                None
            ),
            'showing': (
                'showing {}'.format(self._applescript_list(passed['showing']))
                if 'showing' in passed_keys and len(passed['showing']) > 0 and
                set(passed['showing']) <= set(available_servers) else
                None
            ),
            'editable_url': (
                'editable URL true'
                if 'editable_url' in passed_keys and
                passed['editable_url'] else
                None
            ),
            'alert_type': (
                'as {}'.format(passed['alert_type'])
                if 'alert_type' in passed_keys and
                len(passed['alert_type']) > 0 and
                passed['alert_type'] in available_alert_types else
                None
            ),
            'buttons': (
                'buttons {}'.format(self._applescript_list(passed['buttons']))
                if 'buttons' in passed_keys and
                0 < len(passed['buttons']) < 4 else
                None
            ),
            'default_button': (
                'default button "{}"'.format(passed['default_button'])
                if 'default_button' in passed_keys and
                len(passed['default_button']) > 0 else
                None
            ),
            'cancel_button': (
                'cancel button "{}"'.format(passed['cancel_button'])
                if 'cancel_button' in passed_keys and
                len(passed['cancel_button']) > 0 else
                None
            ),
            'giving_up_after': (
                'giving up after {}'.format(passed['giving_up_after'])
                if 'giving_up_after' in passed_keys else
                None
            ),
            'default_answer': (
                'default answer "{}"'.format(passed['default_answer'])
                if 'default_answer' in passed_keys else
                None
            ),
            'hidden_answer': (
                'hidden answer true'
                if 'hidden_answer' in passed_keys and
                passed['hidden_answer'] else
                None
            ),
            'icon': (
                'with icon {}'.format(
                    self._applescript_alias(passed['icon'])
                    if not passed['icon'] in available_icons and
                    os.path.exists(passed['icon']) else
                    passed['icon']
                )
                if 'icon' in passed_keys else
                None
            ),
            'sound_name': (
                'sound name "{}"'.format(passed['sound_name'])
                if 'sound_name' in passed_keys and
                len(passed['sound_name']) > 0 else
                None
            )

        }
        return ' '.join([v for (k, v,) in extdict.iteritems() if v])

    def choose_application(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': ['title'],
            'custom_options': {
                'title': (basestring,),
                'prompt': (basestring,),
                'multiple_selections_allowed': (bool,),
                'as_': (basestring,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose application {ext}'.format(
                    ext=self._build_passed(_passed)
                )
            ).split(', ')

    def choose_file(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': [],
            'custom_options': {
                'prompt': (basestring,),
                'type': (list, tuple,),
                'default_location': (basestring,),
                'invisibles': (bool,),
                'multiple_selections_allowed': (bool,),
                'showing_package_contents': (bool,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose file {ext}'.format(ext=self._build_passed(_passed))
            ).split(', ')

    def choose_file_name(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': [],
            'custom_options': {
                'prompt': (basestring,),
                'default_name': (list, tuple,),
                'default_location': (basestring,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose file name {ext}'.format(
                    ext=self._build_passed(_passed)
                )
            )

    def choose_folder(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': [],
            'custom_options': {
                'prompt': (basestring,),
                'default_location': (basestring,),
                'invisibles': (bool,),
                'multiple_selections_allowed': (bool,),
                'showing_package_contents': (bool,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose folder {ext}'.format(ext=self._build_passed(_passed))
            ).split(', ')

    def choose_from_list(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': ['list'],
            'custom_options': {
                'list': (list, tuple,),
                'title': (basestring,),
                'prompt': (basestring,),
                'default_items': (list, tuple,),
                'ok_button_name': (basestring,),
                'cancel_button_name': (basestring,),
                'multiple_selections_allowed': (bool,),
                'empty_selection_allowed': (bool,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose from list {list} {ext}'.format(
                    list=self._applescript_list(_passed['list']),
                    ext=self._build_passed(_passed)
                )
            ).split(', ')

    def choose_remote_application(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': [],
            'custom_options': {
                'title': (basestring,),
                'prompt': (basestring,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose remote application {ext}'.format(
                    ext=self._build_passed(_passed)
                )
            )

    def choose_url(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': [],
            'custom_options': {
                'showing': (list, tuple,),
                'editable_url': (bool,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'choose URL {ext}'.format(
                    ext=self._build_passed(_passed)
                )
            )

    def display_alert(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': ['text'],
            'custom_options': {
                'text': (basestring,),
                'message': (basestring,),
                'alert_type': (basestring,),
                'buttons': (list, tuple,),
                'default_button': (basestring,),
                'cancel_button': (basestring,),
                'giving_up_after': (int, float,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            resp = self._osascript(
                'display alert "{text}" {ext}'.format(
                    text=_passed['text'],
                    ext=self._build_passed(_passed)
                )
            ).split(', ')
            retn = dict([tuple(i.split(':')) for i in resp])
            if 'gave up' in retn.keys() and retn['gave up'].lower() == 'true':
                raise DurationExceededException()
            return retn

    def display_dialog(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': ['text'],
            'custom_options': {
                'text': (basestring,),
                'title': (basestring,),
                'default_answer': (basestring,),
                'hidden_answer': (bool,),
                'buttons': (list, tuple,),
                'default_button': (basestring,),
                'cancel_button': (basestring,),
                'giving_up_after': (int, float,),
                'icon': (basestring, int,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            resp = self._osascript(
                'display dialog "{text}" {ext}'.format(
                    text=_passed['text'],
                    ext=self._build_passed(_passed)
                )
            ).split(', ')
            retn = dict([tuple(i.split(':')) for i in resp])
            if 'gave up' in retn.keys() and retn['gave up'].lower() == 'true':
                raise DurationExceededException()
            return retn

    def display_notification(self, **_passed):
        custom_options = {
            'function': inspect.getframeinfo(
                inspect.currentframe()
            )[2].lower(),
            'required_options': ['text'],
            'custom_options': {
                'text': (basestring,),
                'title': (basestring,),
                'subtitle': (basestring,),
                'sound_name': (basestring,),
            }
        }
        _passed = self._format_passed(_passed)
        if self._valid_options(_passed, custom_options):
            return self._osascript(
                'display notification "{text}" {ext}'.format(
                    text=_passed['text'],
                    ext=self._build_passed(_passed)
                )
            )
