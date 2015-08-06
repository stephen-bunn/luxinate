#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
settings

.. module:: settings
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

from __future__ import unicode_literals

import os
import json
import webbrowser

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
import exceptions


class Settings(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __init__(self):
        if not hasattr(self._global, 'ab'):
            raise exceptions.LuxinateImplementationException((
                '{name} requires client to have initialized '
                '`ab` attribute'
            ).format(name=self.__class__.__name__))
        self.storage = os.path.join(
            self._global.ab.workflow_data, 'settings.json'
        )
        if not os.path.exists(self.storage) or \
                len(open(self.storage, 'rb').read()) <= 0:
            self.save(self.storage, self._global.settings_defaults)
        self.load(self.storage)

    def __getstate__(self):
        return {
            'storage': self.storage
        }

    def load(self, path):
        self.settings = json.load(open(path, 'rb'))

    def save(self, path, data):
        json.dump(data, open(path, 'wb'))
        self.load(path)

    def progress_bar(self):
        self.settings['progress'] = not self.settings['progress']
        self.save(self.storage, self.settings)
        self._global.tn_client.notify(
            title='{} Settings'.format(self._global.module_name),
            subtitle='Toggled progress bar {}'.format(
                'ON' if self.settings['progress'] else 'OFF'
            ),
            message=' ',
            sender=self._global.notify_sender,
            group=self._global.notify_group
        )

    def download_directory(self):
        resp = self._global.cd_client.fileselect(
            title='{} Download Directory'.format(self._global.module_name),
            text='Please select a new default download directory...',
            select_only_directories=True,
            with_directory=self.settings['save_to']
        )
        if len(resp) > 0:
            self.settings['save_to'] = resp[0]
            self.save(self.storage, self.settings)
            self._global.tn_client.notify(
                title='{} Settings'.format(self._global.module_name),
                message=self.settings['save_to'],
                subtitle='Changed default download directory',
                sender=self._global.notify_sender,
                group=self._global.notify_group
            )

    def output_template(self):
        resp = self._global.cd_client.inputbox(
            title='{} Output Template'.format(self._global.module_name),
            informative_text=(
                'Set the template used to store downloaded files...'
            ),
            text=self.settings['outtmpl'],
            button1='Save Template',
            button2='Cancel',
            button3='Template Features'
        )
        btn = int(resp[0])
        if btn == 1:
            self.settings['outtmpl'] = resp[1]
            self.save(self.storage, self.settings)
            self._global.tn_client.notify(
                title='{} Settings'.format(self._global.module_name),
                subtitle='Changed download output template',
                message=self.settings['outtmpl'],
                sender=self._global.notify_sender,
                group=self._global.notify_group
            )
        elif btn == 3:
            webbrowser.open(self._global.outtmpl_link)

    # TODO: Find a way to streamline these conversion dropdowns
    def conversion_format(self):
        available_formats = self._global.settings_options['audio_format']
        available_formats.insert(
            0,
            available_formats.pop(
                available_formats.index(self.settings['audio_format'])
            )
        )
        resp = self._global.cd_client.standard_dropdown(
            title='{} Settings'.format(self._global.module_name),
            text='Please select your preferred audio conversion format...',
            items=available_formats,
            height=125,
        )
        if int(resp[0]) == 1:
            new_format = available_formats[int(resp[1])]
            if self.settings['audio_format'] != new_format:
                self.settings['audio_format'] = new_format
                self.save(self.storage, self.settings)
                self._global.tn_client.notify(
                    title='{} Settings'.format(self._global.module_name),
                    subtitle='Modified preferred audio conversion format',
                    message=self.settings['audio_format'],
                    sender=self._global.notify_sender,
                    group=self._global.notify_group
                )

    def conversion_bitrate(self):
        available_bitrates = self._global.settings_options['audio_bitrate']
        available_bitrates.insert(
            0,
            available_bitrates.pop(
                available_bitrates.index(self.settings['audio_bitrate'])
            )
        )
        resp = self._global.cd_client.standard_dropdown(
            title='{} Settings'.format(self._global.module_name),
            text='Please select your preferred audio conversion bitrate...',
            items=available_bitrates,
            height=125,
        )
        if int(resp[0]) == 1:
            new_bitrate = available_bitrates[int(resp[1])]
            if self.settings['audio_bitrate'] != new_bitrate:
                self.settings['audio_bitrate'] = new_bitrate
                self.save(self.storage, self.settings)
                self._global.tn_client.notify(
                    title='{} Settings'.format(self._global.module_name),
                    subtitle='Modified preferred audio conversion bitrate',
                    message=self.settings['audio_bitrate'],
                    sender=self._global.notify_sender,
                    group=self._global.notify_group
                )

    def show_log(self):
        # HACK: Relying on unstable and dynamic log handler at index 0
        self._global._run_subprocess([
            'open', '-a', 'Console.app',
            os.path.abspath(os.path.realpath(
                self.log.handlers[0].baseFilename
            ))
        ])

    def scriptfilter(self):
        _filter = self._global.ab.wrapper('scriptfilter')
        _filter.add(
            title='Download Directory',
            subtitle='Change where downloads are defaultly stored',
            arg='"download_directory"',
            icon=self._global.icons['folder']
        )
        _filter.add(
            title='Progress Bar',
            subtitle='Toggle progress bar {}'.format(
                'OFF' if self.settings['progress'] else 'ON'
            ),
            arg='"progress_bar"',
            icon=(
                self._global.icons['check']
                if self.settings['progress'] else
                self._global.icons['x']
            )
        )
        _filter.add(
            title='Output Template',
            subtitle='Edit the template used to save files',
            arg='"output_template"',
            icon=self._global.icons['tags']
        )
        _filter.add(
            title='Conversion Format',
            subtitle='Edit the preferred audio conversion format',
            arg='"conversion_format"',
            icon=self._global.icons['musical-note']
        )
        _filter.add(
            title='Conversion Bitrate',
            subtitle='Edit the preferred audio conversion bitrate',
            arg='"conversion_bitrate"',
            icon=self._global.icons['headphones']
        )
        _filter.add(
            title='Show {} Log'.format(self._global.module_name),
            subtitle='View the stored log, used for debugging {}'.format(
                self._global.module_name
            ),
            arg='"show_log"',
            icon=self._global.icons['code']
        )
        return _filter

    def handler(self, query):
        # HACK: A possibly dangerous hack, query handler
        querycall = getattr(self, query, None)
        if callable(querycall):
            querycall()
