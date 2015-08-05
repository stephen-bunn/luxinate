#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
emebed

.. module:: emebed
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

import os
import abc
import urllib2

import mutagen.mp3
import mutagen.id3
import mutagen.easyid3

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess


class AbstractTagEmbedder(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __getstate__(self):
        return {}

    @abc.abstractproperty
    def extension(self):
        pass

    @abc.abstractmethod
    def tag(self):
        pass


class MP3TagEmbedder(AbstractTagEmbedder):
    _extension = '.mp3'
    _tags = {
        'title': (basestring,),
        'artist': (basestring,),
        'album': (basestring,),
        'year': (basestring,),
        'comment': (basestring,),
        'track': (basestring,),
        'genre': (basestring,),
        'artwork': (basestring,),
    }
    _artwork_mimetypes = {
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.png': 'image/png'
    }

    def __init__(self, path):
        self.path = path
        if os.path.splitext(self.path)[-1].lower() == self.extension:
            self.mutate = mutagen.mp3.MP3(
                self.path,
                ID3=mutagen.easyid3.EasyID3
            )
        else:
            raise ValueError(
                'unrecognized path `{path}` for `{ext}` embed'.format(
                    name=self.__class__.__name__,
                    mod=self.path,
                    ext=self.extension
                )
            )

    @property
    def extension(self):
        return self._extension

    def tag(self, **kwargs):
        if not self.mutate.tags:
            try:
                self.log.debug(
                    'adding id3 tags to `{path}` ...'.format(path=self.path)
                )
                self.mutate.add_tags()
            except mutagen.id3.error, id3err:
                self.log.error((
                    'error occured when adding id3 tags to '
                    '{path}, {err} ...'.format(
                        path=self.path,
                        err=id3err.message
                    )
                ))

        if not set(kwargs.keys()) <= set(self._tags.keys()):
            for (k, v,) in kwargs.items():
                if k not in self._tags.keys():
                    self.log.debug((
                        'encountered invalid id3 tag `{k}`, '
                        'removing ...'
                    ).format(k=k))
                    del kwargs[k]

        self.mutate.tags.update([
            (k, v,)
            for (k, v,) in kwargs.iteritems()
            if k != 'artwork'
        ])
        self.mutate.save()

        if 'artwork' in kwargs.keys():
            advmutate = mutagen.mp3.MP3(
                self.path,
                ID3=mutagen.id3.ID3
            )
            if not advmutate.tags:
                advmutate.add_tags()
            (mimetype, artwork,) = (None, None,)
            try:
                mimetype = \
                    self._artwork_mimetypes[
                        os.path.splitext(kwargs['artwork'])[-1].lower()
                    ]
            except KeyError:
                self.log.error(
                    'unsupported artwork mimetype `{artwork} ...`'.format(
                        artwork=kwargs['artwork']
                    )
                )
            if mimetype:
                if not os.path.exists(kwargs['artwork']):
                    try:
                        artwork = urllib2.urlopen(kwargs['artwork']).read()
                    except urllib2.URLError:
                        raise ValueError((
                            'couldn\'t find artwork '
                            'resource `{artwork}`'
                        ).format(artwork=kwargs['artwork']))
                else:
                    artwork = open(kwargs['artwork'], 'rb').read()
                if artwork:
                    self.log.debug((
                        'applying APIC artwork id3 tag to `{path}` ...'
                    ).format(path=self.path))
                    advmutate.tags.add(
                        mutagen.id3.APIC(
                            encoding=3,
                            mime=mimetype,
                            type=3,
                            desc=kwargs['artwork'],
                            data=artwork
                        )
                    )
                    advmutate.save()


class Embedder(
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
        self.embedders = {
            '.mp3': MP3TagEmbedder
        }

    def __getstate__(self):
        return {}

    def embed(self, mod, progress_bar=None):
        if progress_bar:
            progress_bar.update(
                percent=100,
                text='【Embedding Tags】{title}'.format(
                    title=mod.info['title']
                )
            )
        for i in mod.embeddable:
            if os.path.exists(i):
                try:
                    self.log.info(
                        'embedding meta info into {mod} ...'.format(mod=mod)
                    )
                    self.embedders[os.path.splitext(i)[-1].lower()](i).tag(
                        title=mod.info['title'],
                        artist=mod.info['uploader'],
                        artwork=mod.info['thumbnail']
                    )
                except KeyError:
                    self.log.warning(
                        'embedder for extension `{ext}` not found ...'.format(
                            ext=os.path.splitext(i)[-1].lower()
                        )
                    )
