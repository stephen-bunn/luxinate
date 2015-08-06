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
import sys
import ast
import time
import shutil
import tempfile

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
import settings
import history

import youtube_dl


class Downloader(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __init__(self):
        self.settings = settings.Settings().settings
        self.history = history.History()

    def __getstate__(self):
        return {}

    def download(self, mod, progress_bar=None):
        self.log.info('downloading {mod} ...'.format(mod=mod))
        yt_options = {
            'format': 'best',
            'logger': None,
            'outtmpl': mod.outtmpl_storage,
            'progress_hooks': []
        }

        def _download_progress_hook(info, progress_bar=progress_bar):
            if progress_bar and info['status'].lower() == 'downloading':
                progress_bar.update(
                    percent=float(info['_percent_str'][:-1]),
                    text='【ETA {eta}】{title}'.format(
                        eta=info['_eta_str'],
                        title=mod.info['title']
                    )
                )

        if progress_bar:
            yt_options['progress_hooks'].append(_download_progress_hook)
        try:
            with youtube_dl.YoutubeDL(yt_options) as ydl:
                ydl.download([mod.info['webpage_url']])
            return [
                os.path.join(os.path.dirname(mod.outtmpl_storage), i)
                for i in os.listdir(os.path.dirname(mod.outtmpl_storage))
            ]
        except Exception, err:
            self._global.cd_client.ok_msgbox(
                title='{} Error'.format(self._global.module_name),
                text='Sorry, an unexpected error occured during download...',
                informative_text=err.message,
                no_cancel=True,
                icon='caution',
            )
            sys.exit(1)
