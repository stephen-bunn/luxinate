#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
handler

.. module:: handler
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-04-25 00:03:13
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

import os
import abc
import time
import shutil
import tempfile

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
import exceptions
import settings
import history
import model
import download
import convert


class AbstractHandler(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    @abc.abstractmethod
    def handle(self):
        pass


class ModelHandler(AbstractHandler):

    def __init__(self, mod):
        self.mod = mod
        if not isinstance(self.mod, model.Model):
            raise exceptions.LuxinateImplementationException(
                '{name} requires model of type {model}'.format(
                    name=self.__class__.__name__,
                    model=model.Model
                )
            )
        if not hasattr(self.mod, 'download_type') or \
                not self.mod.download_type or \
                self.mod.download_type not in self._global.DownloadType:
            self.log.info(
                'defaulting {mod} download type to `{download_type}`'.format(
                    mod=self.mod,
                    download_type=self._global.DownloadType.video
                )
            )
            setattr(self.mod, 'download_type', self._global.DownloadType.video)
        self.settings = settings.Settings().settings
        self.history = history.History()
        self.downloader = download.Downloader()
        self.converter = convert.Converter()
        self._download_methods = {
            True: {
                self._global.DownloadType.video: self._video_multi,
                self._global.DownloadType.audio: self._audio_multi,
                self._global.DownloadType.combi: self._combi_multi,
            },
            False: {
                self._global.DownloadType.video: self._video_single,
                self._global.DownloadType.audio: self._audio_single,
                self._global.DownloadType.combi: self._combi_single
            }
        }
        self.progress_bar = (
            self._global.cd_client.progressbar(
                title='{} Download'.format(self._global.module_name),
                text='Preparing download...',
                percent=0,
                icon_file=self._global.workflow_icon)
            if self.settings['progress'] else None
        )

    def __getstate__(self):
        return {
            'mod': self.mod,
            '_download_methods': self._download_methods,
            'downloader': self.downloader,
            'converter': self.converter
        }

    def _video_single(self):
        self.downloader.download(self.mod, progress_bar=self.progress_bar)

    def _audio_single(self):
        requires_convert = self.mod.info['ext'] not in \
            self._global.common_audio_exts
        tempstore = (
            os.path.join(
                os.path.realpath(
                    tempfile.mkdtemp(
                        suffix=self._global.temp_storage_suffix
                    )
                ),
                os.path.basename(self.mod.render_outtmpl())
            ) if requires_convert else self.mod.outtmpl
        )
        self.mod.outtmpl = tempstore
        self.downloader.download(self.mod, progress_bar=self.progress_bar)
        if requires_convert:
            converted = self.converter.convert(
                self.mod,
                progress_bar=self.progress_bar
            )
            [
                shutil.move(
                    i,
                    os.path.join(
                        self.settings['save_to'], os.path.basename(i)
                    )
                ) for i in converted
            ]
            shutil.rmtree(os.path.dirname(tempstore))

    def _combi_single(self):
        self.downloader.download(self.mod, progress_bar=self.progress_bar)
        self.converter.convert(self.mod, progress_bar=self.progress_bar)

    def _video_multi(self):
        pass

    def _audio_multi(self):
        pass

    def _combi_multi(self):
        pass

    def handle(self):
        self._download_methods[self.mod.multiple][self.mod.download_type]()
        self.history.add(self.mod)
        self.progress_bar.update(
            text='Download completed',
            percent=100
        )
        time.sleep(self._global.progressbar_kill_time_buffer)
        self.progress_bar.finish()
        self._global.tn_client.notify(
            title=self._global.module_name,
            subtitle='Download Completed',
            message=self.mod.info['title'],
            sender=self._global.notify_sender,
            group=self._global.notify_group,
            sound=self._global.notify_sound
        )
