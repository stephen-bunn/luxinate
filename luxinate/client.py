#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
client

.. module:: client
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-06-10 15:28:29
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

from __future__ import unicode_literals

import os
import ast
import socket
import urllib2

from utils import MetaLogged, MetaGlobalAccess
import settings
import history
import service
import resource
import handler
import model


class Client(MetaLogged.Logged, MetaGlobalAccess.GlobalAccess):
    _ab = service.AlfredBundlerService().service

    def __init__(self):
        self._global.log = self._ab.logger(self.__class__.__name__)
        if not hasattr(self._global, 'ab'):
            setattr(self._global, 'ab', self._ab)
        self.log.debug(
            'initializing `{}` for `{}` ...'.format(
                self.__class__.__name__,
                self._global.module_name
            )
        )
        self._global._build_icons()
        self._global._build_wrappers()

        self._resource_manager = resource.ResourceManager()
        self._ffmpeg_resource = resource.FFMpegResource()
        if not self._resource_manager.is_registered(self._ffmpeg_resource):
            self._resource_manager.register(self._ffmpeg_resource)
        self._resource_manager.update()

        try:
            import youtube_dl
            self.yt = youtube_dl
        except ImportError:
            raise exceptions.LuxinateRequirementException((
                '{name} requires the youtube-dl module '
                'to be successfully imported, failed'
            ).format(name=self.__class__.__name__))

        self._settings = settings.Settings()
        self._history = history.History()

    def handle(self, info):
        handler.ModelHandler(model.Model(info=info)).handle()

    def settings(self):
        return self._settings.scriptfilter()

    def history(self, query):
        return self._history.scriptfilter(query)

    def default(self, url):
        _filter = self._global.ab.wrapper('scriptfilter')
        if self._global._has_connection():
            if self._global._match_url(url):
                try:
                    info = self.yt.YoutubeDL({
                        'logtostderr': True
                    }).extract_info(url, download=False)
                    requires_convert = info['ext'] not in \
                        self._global.common_audio_exts
                    if requires_convert:
                        _filter.add(
                            title='Download Video',
                            subtitle=info['title'],
                            arg=unicode(self._global._merge_dicts(
                                info, dict([('download_type', 0x01,)])
                            )),
                            icon=self._global.icons['video']
                        )
                    _filter.add(
                        title='Download Audio',
                        subtitle=info['title'],
                        arg=unicode(self._global._merge_dicts(
                            info, dict([('download_type', 0x02,)])
                        )),
                        icon=self._global.icons['audio']
                    )
                    if requires_convert:
                        _filter.add(
                            title='Download Video & Audio',
                            subtitle=info['title'],
                            arg=unicode(
                                self._global._merge_dicts(
                                    info, dict([('download_type', 0x04,)])
                                )
                            ),
                            icon=self._global.icons['ellipses']
                        )
                except self.yt.utils.DownloadError, yterr:
                    _filter.add(
                        title='Unsupported URL',
                        subtitle=yterr.message,
                        arg=None,
                        icon=self._global.icons['unsupported']
                    )
                except socket.timeout:
                    _filter.add(
                        title='Retrieval socket timed out',
                        subtitle='Please retry entering your query',
                        arg=None,
                        icon=self._global.icons['link-broken']
                    )
            else:
                _filter.add(
                    title='Invalid URL',
                    subtitle='The given URL is an invalid link',
                    arg=None,
                    icon=self._global.icons['link-broken']
                )
        else:
            _filter.add(
                title='No connection',
                subtitle='Please check your internet connection',
                arg=None,
                icon=self._global.icons['link-broken']
            )
        return _filter
