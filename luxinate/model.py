#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
model

.. module:: model
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

try:
    import youtube_dl
except ImportError:
    raise exceptions.LuxinateImplementationException(
        'access to "{file_}" failed due to failed youtube_dl import'.format(
            file_=__file__
        )
    )

from utils import MetaSerializable, MetaLogged, MetaGlobalAccess
import exceptions
import settings
import history
import download
import convert
import embed


class AbstractModel(
    MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __str__(self):
        return '{name}({attrs})'.format(
            name=self.__class__.__name__,
            attrs=', '.join([
                '{k}="{v}"'.format(k=k, v=v)
                for (k, v,) in self.__getstate__().iteritems()
            ])
        )

    def __getstate__(self):
        return {}

    @abc.abstractproperty
    def storage(self):
        pass

    @abc.abstractmethod
    def handle(self):
        pass

    @abc.abstractmethod
    def clean(self):
        pass


class LuxinateModel(AbstractModel):
    (
        _url, _info, _storage, _embeddable, _convertable,
        _save_to, _outtmpl, _outtmpl_storage,
        _outtmpl_rendered, _outtmpl_storage_rendered,
        _multiple, _media_type, _download_type, _convert_type,
    ) = (None,) * 14

    def __init__(self, url, info=None):
        self.log.debug('building new `{name}` ...'.format(
            name=self.__class__.__name__)
        )
        self.settings = settings.Settings().settings
        self.history = history.History()
        self.downloader = download.Downloader()
        self.converter = convert.Converter()
        self.embedder = embed.Embedder()

        (self._url, self._info,) = (url, info,)

    def __str__(self):
        return '{name}({attrs})'.format(
            name=self.__class__.__name__,
            attrs='url="{url}"'.format(url=self.url)
        )

    def __getstate__(self):
        return {
            '_url': self.url,
            '_info': self.info,
            '_storage': self.storage,
            '_outtmpl': self.outtmpl,
            '_embeddable': self.embeddable,
            '_multiple': self.multiple,
            '_media_type': self.media_type,
            '_download_type': self.download_type,
            '_convert_type': self.convert_type
        }

    @property
    def url(self):
        if not hasattr(self, '_url') \
                or not self._url or not isinstance(self._url, basestring):
            if hasattr(self, 'info'):
                self._url = self.info['webpage_url']
        return self._url

    @property
    def info(self):
        if not hasattr(self, '_info') \
                or not self._info or not isinstance(self._info, dict):
            if hasattr(self, 'url'):
                if self._global._has_connection() and \
                        self._global._match_url(self.url):
                    self.log.info(
                        'extracting information from `{url}` ...'.format(
                            url=self.url
                        )
                    )
                    self._info = youtube_dl.YoutubeDL({
                        'logtostderr': True,
                        'extract_flat': True,
                    }).extract_info(self.url, download=False)
            else:
                self.log.error((
                    '`{name}.info` count not be built due to '
                    'missing property `url` ...'
                ).format(name=self.__class__.__name__))
        return self._info

    @property
    def storage(self):
        if not hasattr(self, '_storage') \
                or not self._storage \
                or not os.path.exists(self._storage) \
                or not os.path.isdir(self._storage):
            if hasattr(self, 'info'):
                self._storage = os.path.realpath(
                    tempfile.mkdtemp(
                        prefix='{}-'.format(self._global.module_bundle),
                        suffix='-{}'.format(self.info['id'])
                    )
                )
            else:
                self.log.error((
                    '`{name}.storage` could not be built due to '
                    'missing property `info` ...'
                ).format(name=self.__class__.__name__))
        return self._storage

    @property
    def save_to(self):
        if not hasattr(self, '_save_to') \
                or not self._save_to \
                or not isinstance(self._save_to, basestring):
            self._save_to = os.path.abspath(
                os.path.realpath(self.settings['save_to'])
            )
        return self._save_to

    @property
    def outtmpl(self):
        if not hasattr(self, '_outtmpl') \
                or not self._outtmpl \
                or not isinstance(self._outtmpl, basestring):
            if hasattr(self, 'save_to'):
                self._outtmpl = os.path.join(
                    self.save_to, self.settings['outtmpl']
                )
        return self._outtmpl

    @property
    def outtmpl_storage(self):
        if not hasattr(self, '_outtmpl_storage') \
                or not self._outtmpl_storage \
                or not isinstance(self._outtmpl_storage, basestring):
            if hasattr(self, 'storage'):
                self._outtmpl_storage = os.path.join(
                    self.storage, self.settings['outtmpl']
                )
        return self._outtmpl_storage

    @property
    def outtmpl_rendered(self):
        if not hasattr(self, '_outtmpl_rendered') \
                or not self._outtmpl_rendered \
                or not isinstance(self._outtmpl_rendered, basestring):
            if hasattr(self, 'info') and hasattr(self, 'outtmpl'):
                self._outtmpl_rendered = self.outtmpl % self.info
        return self._outtmpl_rendered

    @property
    def outtmpl_storage_rendered(self):
        if not hasattr(self, '_outtmpl_storage_rendered') \
                or not self._outtmpl_storage_rendered \
                or not isinstance(self._outtmpl_storage_rendered, basestring):
            if hasattr(self, 'storage') and hasattr(self, 'outtmpl_rendered'):
                self._outtmpl_storage_rendered = os.path.join(
                    self.storage, os.path.basename(self.outtmpl_rendered)
                )
        return self._outtmpl_storage_rendered

    @property
    def multiple(self):
        if not hasattr(self, '_multiple') \
                or not self._multiple or not isinstance(self._multiple, bool):
            if hasattr(self, 'info'):
                self._multiple = ('_type' in self.info.keys())
            else:
                self.log.error((
                    '`{name}.multiple` could not be built due to '
                    'missing property `info` ...'
                ).format(name=self.__class__.__name__))
        return self._multiple

    @property
    def media_type(self):
        if not hasattr(self, '_media_type') \
                or not self._media_type \
                or not isinstance(self._media_type, self._global.MediaType):
            if hasattr(self, 'info'):
                self._media_type = (
                    self._global.MediaType.audio
                    if self.info['ext'].lower() in
                    self._global.common_audio_exts else
                    self._global.MediaType.video
                )
            else:
                self.log.error((
                    '`{name}.multiple` could not be built due to '
                    'missing property `info` ...'
                ).format(name=self.__class__.__name__))
        return self._media_type

    @property
    def download_type(self):
        if not hasattr(self, '_download_type') \
                or not self._download_type \
                or not isinstance(
                    self._download_type, self._global.DownloadType
                ):
            if 'download_type' not in self.info.keys():
                default_type = (
                    self._global.DownloadType.audio
                    if self.media_type == self._global.MediaType.audio else
                    self._global.DownloadType.video
                )
                self.log.warning((
                    'defaulting `{name}.download_type` to '
                    '`{dtype}` ...'
                ).format(
                    name=self.__class__.__name__,
                    dtype=default_type
                ))
                self._download_type = default_type
            else:
                self._download_type = self._global._download_type(
                    self.info['download_type']
                )
        return self._download_type

    @property
    def convert_type(self):
        if not hasattr(self, '_convert_type') \
                or not self._convert_type \
                or not isinstance(
                    self._convert_type, self._global.ConvertType
                ):
            default_type = (
                self._global.ConvertType.video2audio
                if self.download_type == self._global.DownloadType.video else
                self._global.ConvertType.audio2audio
            )
            self.log.warning(
                'defaulting `{name}.convert_type` to `{dtype}` ...'.format(
                    name=self.__class__.__name__,
                    dtype=default_type
                )
            )
            self._convert_type = default_type
        return self._convert_type

    @property
    def convertable(self):
        if not hasattr(self, '_convertable') \
                or not self._convertable \
                or not isinstance(self._convertable, list):
            self._convertable = []
        return self._convertable

    @property
    def embeddable(self):
        if not hasattr(self, '_embeddable') \
                or not self._embeddable \
                or not isinstance(self._embeddable, list):
            self._embeddable = []
        return self._embeddable

    def _single_video(self, progress_bar=None):
        self.embeddable.extend(
            self.downloader.download(self, progress_bar=progress_bar)
        )
        self.embedder.embed(self, progress_bar=progress_bar)
        self.log.debug(
            'adjusting modelspace file locations for `{func}` ...'.format(
                func=self._single_video.__name__
            )
        )
        shutil.move(
            self.outtmpl_storage_rendered,
            self.outtmpl_rendered
        )

    def _single_audio(self, progress_bar=None):
        downloaded = self.downloader.download(self, progress_bar=progress_bar)
        if self.media_type != self._global.MediaType.video:
            self.embeddable.extend(downloaded)
        else:
            self.convertable.extend(downloaded)
            self.embeddable.extend(
                self.converter.convert(self, progress_bar=progress_bar)
            )
        time.sleep(self._global.ffmpeg_progress_exit_time_buffer)
        self.embedder.embed(self, progress_bar=progress_bar)
        self._info['ext'] = os.path.splitext(self.embeddable[-1])[-1][1:]
        self.log.debug(
            'adjusting modelspace file locations for `{func}` ...'.format(
                func=self._single_audio.__name__
            )
        )
        shutil.move(
            os.path.realpath(self.embeddable[-1]),
            os.path.join(self.save_to, os.path.basename(self.embeddable[-1]))
        )

    def _single_combi(self, progress_bar=None):
        downloaded = self.downloader.download(self, progress_bar=progress_bar)
        self.convertable.extend(downloaded)
        converted = self.converter.convert(self, progress_bar=progress_bar)
        self.embeddable.extend(downloaded + converted)
        time.sleep(self._global.ffmpeg_progress_exit_time_buffer)
        self.embedder.embed(self, progress_bar=progress_bar)
        self.log.debug(
            'adjusting modelspace file locations for `{func}` ...'.format(
                func=self._single_combi.__name__
            )
        )
        for i in os.listdir(self.storage):
            shutil.move(
                os.path.join(self.storage, i),
                os.path.join(self.save_to, i)
            )

    def _multi_video(self, progress_bar=None):
        pass

    def _multi_audio(self, progress_bar=None):
        pass

    def _multi_combi(self, progress_bar=None):
        pass

    def handle(self):
        handlers = {
            False: {
                self._global.DownloadType.video: self._single_video,
                self._global.DownloadType.audio: self._single_audio,
                self._global.DownloadType.combi: self._single_combi,
            },
            True: {
                self._global.DownloadType.video: self._multi_video,
                self._global.DownloadType.audio: self._multi_audio,
                self._global.DownloadType.combi: self._multi_combi,
            }
        }
        progress_bar = (
            self._global.cd_client.progressbar(
                title='{} Download'.format(self._global.module_name),
                text='Preparing download...',
                percent=0,
                icon_file=self._global.workflow_icon
            )
            if self.settings['progress'] else
            None
        )
        if not progress_bar:
            self._global.tn_client.notify(
                title=self._global.module_name,
                subtitle='Starting Download',
                message=self.info['title'],
                sender=self._global.notify_sender,
                group=self.info['id'],
            )
        handlers[self.multiple][self.download_type](progress_bar=progress_bar)
        self.history.add(self)
        if progress_bar:
            progress_bar.update(
                text='Download completed...',
                percent=100
            )
            time.sleep(self._global.progressbar_kill_time_buffer)
            progress_bar.finish()
        self.clean()
        self._global.tn_client.notify(
            title=self._global.module_name,
            subtitle='Download Completed',
            message=self.info['title'],
            sender=self._global.notify_sender,
            group=self.info['id'],
            sound=self._global.notify_sound
        )

    def clean(self):
        self.log.info('destroying {mod} ...'.format(mod=self))
        if hasattr(self, '_storage') \
                and self._storage and os.path.exists(self._storage):
            self.log.debug(
                'removing {mod} storage at `{store}` ...'.format(
                    mod=self,
                    store=self._storage
                )
            )
            shutil.rmtree(self._storage)
