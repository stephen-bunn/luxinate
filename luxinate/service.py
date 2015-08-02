#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
service

.. module:: service
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-06-10 15:28:29
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

import os
import sys
import abc
import imp
import urllib2

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
from utils import applescript_dialog


class AbstractService(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.serialhandler()

    def __getstate__(self):
        return {
            'storage': self.storage
        }

    @abc.abstractproperty
    def storage(self):
        pass

    @abc.abstractproperty
    def valid(self):
        pass

    @property
    def service(self):
        return self.bootstrap()

    @abc.abstractmethod
    def bootstrap(self):
        pass


class AlfredBundlerService(AbstractService):
    _available_hosts = (
        ('https://raw.githubusercontent.com/'
            'ritashugisha/alfred-bundler/devel/bundler/bundlets/bundler.py'),
        ('https://raw.githubusercontent.com/'
            'shawnrice/alfred-bundler/devel/bundler/bundlets/bundler.py'),
    )
    _applescript = applescript_dialog.AppleScriptDialog(debug=True)

    def _retrieve(self):
        self.log.debug(
            'trying to retrieve `{}` ...'.format(self.__class__.__name__)
        )
        for host in self._available_hosts:
            self.log.debug(
                'attempting to read from bundler host `{}` ...'.format(host)
            )
            try:
                response = urllib2.urlopen(host)
                if response.code == 200:
                    with open(self.storage, 'wb') as f:
                        f.write(response.read())
                    break
            except Exception:
                continue
        return self.valid

    @property
    def storage(self):
        return os.path.join(self._global.outer_base_path, 'bundler.py')

    @property
    def valid(self):
        return os.path.exists(self.storage) and os.path.isfile(self.storage)

    def bootstrap(self):
        if not self.valid:
            if not self._retrieve():
                # the bundler couldnt be retrieved, raise a critcal user alert
                self.log.critical((
                    '`{}` bootstrap failed to download the service '
                    'from all hosts {} ...'
                ).format(
                    self.__class__.__name__,
                    self._available_hosts
                ))
                try:
                    self._applescript.display_alert(
                        text='Failed bundler retrieval',
                        message=(
                            '{module} relies on {service}\n\n'
                            'Since the retrieval of this service failed, '
                            'please let the author know ASAP...\n\n'
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
                # kill everything, critical failure, AB couldn't be retrieved
                sys.exit(1)
        self.log.info('bootstrapping `{}` ...'.format(self.__class__.__name__))
        # load the bundler from its source using py:module imp
        boot = imp.load_source('AlfredBundler', self.storage)
        try:
            return boot.AlfredBundler()
        except boot.InstallationError, err:
            # catch bundler installation errors and raise a user viewable alert
            try:
                self.log.warning(
                    'user has caused `{}` installation error ...'.format(
                        self.__class__.__name__
                    )
                )
                self._applescript.display_alert(
                    text=err.message,
                    message=(
                        '{module} relies on {service}\n\n'
                        'You will be prompted to install this service again '
                        'next time you attempt to use {module}'
                    ).format(
                        module=self._global.module_name,
                        service=self.__class__.__name__
                    ),
                    buttons=['Ok'],
                    giving_up_after=5
                )
            except applescript_dialog.AppleScriptException:
                pass
            # kill everything because the user denied installation to AB
            sys.exit(0)
