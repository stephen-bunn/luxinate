#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
download

.. module:: download
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

import os
import ast
import time
import shutil
import tempfile

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
from settings import Settings
from history import History
from convert import Converter

import youtube_dl


class Downloader(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __init__(self):
        if not hasattr(self._global, 'ab'):
            raise exceptions.LuxinateImplementationException((
                '{name} requires client to have initialized '
                'alfred-bundler attribute'
            ).format(name=self.__class__.__name__))
        self.settings = Settings().settings
        self.history = History()
        self.converter = Converter()

    def __getstate__(self):
        return {}

    def download(self, mod, progress_bar=None):
        self.log.info('downloading {mod} ...'.format(mod=mod))
        yt_options = {
            'format': 'best',
            'logger': None,
            'outtmpl': mod.outtmpl,
            'progress_hooks': []
        }

        def _download_progress_hook(info, progress_bar=progress_bar):
            if progress_bar and info['status'].lower() == 'downloading':
                progress_bar.update(
                    percent=float(info['_percent_str'][:-1]),
                    text='【ETA {eta}】{title}'.format(
                        eta=info['_eta_str'],
                        title=os.path.basename(mod.info['title'])
                    )
                )

        if progress_bar:
            yt_options['progress_hooks'].append(_download_progress_hook)
        with youtube_dl.YoutubeDL(yt_options) as ydl:
            ydl.download([mod.info['webpage_url']])
        return mod.outtmpl_rendered
