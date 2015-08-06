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
    _extension = 'mp3'
    _tags = {
        'title': mutagen.id3.TIT2,
        'artist': mutagen.id3.TPE1,
        'comment': mutagen.id3.COMM,
        'url': mutagen.id3.LINK,
        'artwork': mutagen.id3.APIC,
    }
    _artwork_mimetypes = {
        'jpeg': 'image/jpeg',
        'jpg': 'image/jpeg',
        'png': 'image/png'
    }

    def __init__(self, path):
        (self.path, self.mutate,) = (path, None,)
        if os.path.splitext(self.path)[-1][1:].lower() == self.extension:
            self.mutate = mutagen.mp3.MP3(
                self.path,
                ID3=mutagen.id3.ID3
            )
        else:
            self.log.error(
                'unrecognized file `{path}` for `{ext}` embed ...'.format(
                    path=self.path,
                    ext=self.extension
                )
            )

    @property
    def extension(self):
        return self._extension

    def tag(self, **kwargs):
        if hasattr(self, 'mutate') and self.mutate is not None:
            if self.mutate.tags:
                self.log.debug(
                    'removing present id3 tags from `{path}` ...'.format(
                        path=self.path
                    )
                )
                self.mutate.delete()
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

            for (k, v,) in kwargs.iteritems():
                k = k.lower()
                if k in self._tags.keys():
                    if v:

                        if k == 'artwork' and isinstance(v, basestring):
                            (mimetype, artwork,) = (None,) * 2
                            try:
                                mimetype = \
                                    self._artwork_mimetypes[
                                        os.path.splitext(v)[-1][1:].lower()
                                    ]
                            except KeyError:
                                self.log.error((
                                    'unsupported artwork mimetype for artwork '
                                    '`{v}` ...'
                                ).format(v=v))
                                continue
                            if not os.path.exists(v):
                                self.log.debug((
                                    'evaluating artwork `{v}` as '
                                    'url path ...'
                                ).format(v=v))
                                try:
                                    artwork = urllib2.urlopen(v).read()
                                except urllib2.URLError:
                                    self.log.error((
                                        'could not read artwork from resource '
                                        '`{v}` ...'
                                    ).format(v=v))
                                    continue
                            else:
                                artwork = open(v, 'rb').read()
                            if artwork is not None:
                                self.mutate.tags.add(
                                    self._tags[k](
                                        encoding=3,
                                        type=3,
                                        mime=mimetype,
                                        desc=v,
                                        data=artwork
                                    )
                                )

                        elif k == 'url' and isinstance(v, basestring):
                            self.mutate.tags.add(
                                self._tags[k](
                                    encoding=3,
                                    url=v
                                )
                            )

                        else:
                            if isinstance(v, basestring):
                                self.mutate.tags.add(
                                    self._tags[k](
                                        encoding=3,
                                        text=v
                                    )
                                )

            self.log.debug('saving passed tags to `{path}` ...'.format(
                path=self.path
            ))
            self.mutate.save(filename=self.path)

        else:
            self.log.error(
                'missing `mutagen.mp3` instance `mutate`, ignoring tags ...'
            )


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
            'mp3': MP3TagEmbedder
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
        self.log.info('embedding meta info into {mod} ...'.format(mod=mod))
        for i in mod.embeddable:
            if os.path.exists(i):
                try:
                    self.embedders[os.path.splitext(i)[-1][1:].lower()](i).tag(
                        title=mod.info['title'],
                        artist=mod.info['uploader'],
                        url=mod.info['webpage_url'],
                        artwork=(
                            mod.info['thumbnail']
                            if 'thumbnail' in mod.info.keys() else
                            None
                        ),
                        comment=self._global.default_comment,
                    )
                except KeyError:
                    self.log.warning(
                        'embedder for extension `{ext}` not found ...'.format(
                            ext=os.path.splitext(i)[-1][1:].lower()
                        )
                    )
