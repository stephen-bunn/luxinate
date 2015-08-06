#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
resource

.. module:: resource
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-06-10 15:28:29
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

import os
import sys
import abc
import bs4
import time
import urllib2
import zipfile
import tempfile

try:
    import cPickle as pickle
except ImportError:
    import pickle

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
from utils import applescript_dialog


class ResourceManager(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __init__(self, delay=432000):
        self.delay = delay
        self.resource_path = os.path.join(
            self._global.ab.workflow_data, 'resources'
        )
        if not os.path.exists(self.resource_path) or \
                not os.path.isdir(self.resource_path):
            os.makedirs(self.resource_path, 0775)
        self.resource_info_path = os.path.join(
            self.resource_path, 'resources.pickle'
        )
        if not os.path.exists(self.resource_info_path) or \
                len(open(self.resource_info_path, 'rb').read()) <= 0:
            self.save(
                self.resource_info_path,
                {
                    '_delay': self.delay,
                    '_last_updated': time.time()
                }
            )
        self.load(self.resource_info_path)

    def __getstate__(self):
        return {
            'resource_info': self.resource_info,
            'resource_info_path': self.resource_info_path
        }

    def load(self, path):
        self.resource_info = pickle.load(open(path, 'rb'))

    def save(self, path, data):
        pickle.dump(data, open(path, 'wb'))
        self.load(path)

    def is_registered(self, resource):
        return resource.__class__.__name__ in self.resource_info.keys()

    def register(self, resource):
        _resource_info = self.resource_info
        if isinstance(resource, AbstractResource):
            if not self.is_registered(resource):
                self.log.debug(
                    'registering `{}` to `{}` ...'.format(
                        resource.__class__.__name__,
                        self.resource_info_path

                    )
                )
                _resource_info[resource.__class__.__name__] = {
                    'etag': resource.retrieve_etag(),
                    'obj': resource
                }
                self.save(self.resource_info_path, _resource_info)
            else:
                self.log.debug(
                    '`{}` has already been registered ...'.format(
                        resource.__class__.__name__
                    )
                )
        else:
            self.log.error((
                'registration of `{}` failed due to the object '
                'not being an instance of `AbstractResource` ...'
            ).format(self.__class__.__name__))

    def update(self, force=False):
        if (time.time() - self.resource_info['_last_updated']) >= \
                self.resource_info['_delay'] or force:
            self.log.debug('checking for registered resource updates ...')
            updatable_resources = []
            for (name, data,) in self.resource_info.iteritems():
                if isinstance(data, dict):
                    current_etag = data['obj'].retrieve_etag()
                    if data['etag'] != current_etag:
                        self.log.debug('`{}` requires update ...'.format(name))
                        updatable_resources.append(name)
            if len(updatable_resources) > 0:
                resp = self._global.cd_client.msgbox(
                    title=self._global.module_name,
                    text=(
                        'Updates are available for {} resource{}'
                    ).format(
                        len(updatable_resources),
                        ('s' if len(updatable_resources) > 1 else '')
                    ),
                    informative_text=(
                        '\t{}'.format('\n\t'.join(updatable_resources))
                    ),
                    button1='Update',
                    button2='Cancel',
                )
                if int(resp[0]) == 1:
                    for (name, data,) in self.resource_info.iteritems():
                        if name in updatable_resources:
                            data['obj'].update()
                            data['etag'] = data['obj'].retrieve_etag()
                    self.resource_info['_last_updated'] = time.time()
                    self.save(self.resource_info_path, self.resource_info)
        else:
            self.log.debug(
                'next resource update check is in ({} seconds)'.format(
                    (
                        (
                            self.resource_info['_last_updated'] +
                            self.resource_info['_delay']
                        ) - time.time()
                    )
                )
            )


class AbstractResource(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):
    __metaclass__ = abc.ABCMeta
    # TODO: add in the ability to update and check for updates on time delay

    def __init__(self):
        if not os.path.exists(self.resource_path) or \
                not os.path.isdir(self.resource_path):
            os.makedirs(self.resource_path, 0775)
        self.serialhandler()

    def __getstate__(self):
        return {
            'storage': self.storage,
            'resource': self.resource
        }

    @property
    def resource_path(self):
        return os.path.join(
            self._global.ab.workflow_data,
            'resources',
            self.__class__.__name__
        )

    @abc.abstractproperty
    def storage(self):
        pass

    @abc.abstractproperty
    def valid(self):
        pass

    @abc.abstractproperty
    def resource(self):
        pass

    @abc.abstractmethod
    def retrieve(self):
        pass

    @abc.abstractmethod
    def retrieve_etag(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class FFMpegResource(AbstractResource):
    _applescript = applescript_dialog.AppleScriptDialog(debug=True)

    def __init__(self):
        self._host = self._global.ffmpeg_binary_host

    @property
    def storage(self):
        return os.path.join(self.resource_path, 'ffmpeg')

    @property
    def valid(self):
        return os.path.exists(self.storage) and \
            os.path.isfile(self.storage) and os.access(self.storage, os.X_OK)

    @property
    def resource(self):
        if not self.valid:
            if not self.retrieve():
                raise EnvironmentError()
        return self.storage

    def retrieve(self):
        # TODO: desperately needs to have some kind of backup resource
        # FIXME: clean, stabalize, and add user alerts
        self.log.debug(
            'tring to retrieve `{}` from `{}` ...'.format(
                self.__class__.__name__,
                self._host
            )
        )
        # web spider results dictionary
        results = {}
        # HACK: this is a messy way to retrieve downloads, need stable download
        # use bs4 to walk host's site to retrieve dictionary of download urls
        soup = bs4.BeautifulSoup(
            urllib2.urlopen(self._host).read(),
            'lxml'
        )
        for stack in soup.find_all('div', class_='stacks_div'):
            bit = None
            for title in stack.find_all('div', id='titlep'):
                for typ in title.find_all('strong'):
                    if 'bit' in typ.text:
                        # retrieve the bit orientation from the column stack
                        bit = int(typ.text.split('-')[0])
            for dload in stack.find_all('div', class_='grey dload'):
                for link in dload.find_all('a'):
                    # set the download url to the value of the stack bit key
                    results[bit] = os.path.join(self._host, link.get('href'))

        # download the binaries to the storage directory
        f = tempfile.TemporaryFile(dir=self._global.ab.workflow_data)
        try:
            resp = (
                urllib2.urlopen(results[64])
                if 64 in results.keys() and self._global.bit64 else
                (
                    urllib2.urlopen(results[32])
                    if 32 in results.keys() and self._global.bit32 else
                    None
                )
            )
        except Exception:
            self.log.critical((
                '`{}` web spider failed to capture download urls from `{}` ...'
            ).format(
                self.__class__.__name__,
                self._host
            ))
            try:
                self._applescript.display_alert(
                    text='{} Download Failed'.format(self.__class__.__name__),
                    message=(
                        '{module} relies on {service}\n\n'
                        'The web spider used to crawl and retrieve {service} '
                        'binaries failed to capture download URLs.\n\n'
                        'Please let the author know ASAP...\n\n'
                        '{author} ({contact})'
                    ).format(
                        module=self._global.module_name,
                        service=self.__class__.__name__,
                        author=self._global.author_name,
                        contact=self._global.author_email
                    ),
                    buttons=['Ok'],
                    alert_type='critical'
                )
            except applescript_dialog.AppleScriptException:
                pass
            # kill everything because spider couldn't collect valid downloads
            sys.exit(1)
        if resp and resp.code == 200:
            self.log.debug((
                'downloading `{}` binaries for {}bit host machine '
                'from `{}` ...'
            ).format(
                self.__class__.__name__,
                ('64' if self._global.bit64 else '32'),
                resp.url
            ))
            f.write(resp.read())
            zipped = zipfile.ZipFile(f)
            zipped.extractall(self.resource_path)
            # chmod all extracted files as executable (+x)
            [
                os.chmod(os.path.join(self.resource_path, i), 0755)
                for i in zipped.namelist()
            ]
        else:
            try:
                self.log.critical((
                    '`{}` web spider provided invalid download urls '
                    'from `{}` ...'
                ).format(
                    self.__class__.__name__,
                    self._host
                ))
                self._applescript.display_alert(
                    text='{} Download Failed'.format(self.__class__.__name__),
                    message=(
                        '{module} relies on {service}\n\n'
                        'The web spider used to crawl and retrieve {service} '
                        'binaries provided invalid download URLs.\n\n'
                        'Please let the author know ASAP...\n\n'
                        '{author} ({contact})'
                    ).format(
                        module=self._global.module_name,
                        service=self.__class__.__name__,
                        author=self._global.author_name,
                        contact=self._global.author_email
                    ),
                    buttons=['Ok'],
                    alert_type='critical'
                )
            except applescript_dialog.AppleScriptException:
                pass
            # kill everything because spider provided bad download urls
            sys.exit(1)
        f.close()
        return self.valid

    def retrieve_etag(self):
        return urllib2.build_opener().open(
            urllib2.Request(self._host)
        ).headers.dict['etag'].replace('"', '')

    def update(self):
        self.log.debug(
            'updating `{}` resource ...'.format(self.__class__.__name__)
        )
        self.retrieve()
