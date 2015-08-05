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

from utils import MetaSerializable, MetaLogged, MetaGlobalAccess
import exceptions
import settings

import youtube_dl


class Model(
    MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __init__(self, info=None, url=None, download_type=None):
        if not hasattr(self._global, 'ab'):
            raise exceptions.LuxinateImplementationException((
                '{name} requires client to have initialized '
                'alfred-bundler attribute'
            ).format(name=self.__class__.__name__))
        self.settings = settings.Settings().settings

        self.info = info
        self.url = url
        self.download_type = download_type
        self.outtmpl = os.path.join(
            self.settings['save_to'], self.settings['outtmpl']
        )
        self._outtmpl = self.outtmpl
        self.embeddable = []

        if not self.info or not isinstance(self.info, dict):
            if not self.url or not isinstance(self.url, basestring):
                raise exceptions.LuxinateImplementationException((
                    'if missing generated media `info`, '
                    'model requires at least `url`'
                ))
            if not self._global._has_connection() or \
                    not self._global._match_url(self.url):
                raise exceptions.LuxinateException((
                    '{name} couldn\'t successfully fetch resource '
                    '"{url}"'
                ).format(name=self.__class__.__name__, url=self.url))
            self.info = youtube_dl.YoutubeDL({
                'logtostderr': True,
                'extract_flat': True
            }).extract_info(self.url, download=False)
        if not self.download_type:
            if 'download_type' not in self.info.keys():
                raise exceptions.LuxinateImplementationException((
                    'unspecified `download_type`, '
                    'resulting operations dangerous, killing'
                ))
            else:
                self.download_type = \
                    self._global._download_type(self.info['download_type'])
        self.url = self.info['webpage_url']
        self.multiple = ('_type' in self.info.keys())

    def __str__(self):
        return '{name}({attrs})'.format(
            name=self.__class__.__name__,
            attrs=', '.join([
                '{k}="{v}"'.format(k=k, v=v)
                for (k, v,) in self.__getstate__().iteritems()
                if k != 'info'
            ])
        )

    def __getstate__(self):
        return {
            'url': self.url,
            'info': self.info,
            'multiple': self.multiple,
            'download_type': self.download_type
        }

    @property
    def outtmpl_rendered(self):
        if self.info and isinstance(self.info, dict):
            return self.outtmpl % self.info
        return None

    @property
    def _outtmpl_rendered(self):
        if self.info and isinstance(self.info, dict):
            return self._outtmpl % self.info
        return None

    @property
    def downloaded(self):
        return os.path.exists(self.outtmpl_rendered)
