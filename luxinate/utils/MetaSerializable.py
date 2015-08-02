#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
MetaSerializable

.. module:: MetaSerializable
    :platform: Windows, Linux, MacOSX
    :synopsis: Adds serialization features to subclasses (non-portable).
    :created: 2015-06-16 10:40:06
    :modified: 2015-06-19 10:52:44
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

import os
import abc
try:
    import cPickle as pickle
except ImportError:
    import pickle

import MetaLogged
import MetaGlobalAccess


class Serializable(MetaLogged.Logged, MetaGlobalAccess.GlobalAccess, object):
    """ Adds several serialization features to it's subclasses.

    This superclass will add serialization features in order to allow a
    subclass to serialize and store it's current state for future restoration.

    .. note::
        This class is not portable. Dependencies follow below:
            - MetaGlobalAccess.GlobalAccess
            - MetaLogged.Logged
            - __prgm__.Globals
            - __prgm__.Globals -> serial_path

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __getstate__(self):
        pass

    @property
    def serialname(self):
        """ The name of the subclass, either attribute `name` or class name.
        """
        return (
            self.name if hasattr(self, 'name') else self.__class__.__name__
        )

    @property
    def serial(self):
        """ The system path to which the serialized class will be stored.
        """
        return os.path.join(
            self._global.serial_path,
            '{}.serial'.format(self.serialname)
        )

    def serialized(self):
        """ Used to evaluate if the subclass is serialized.

        :returns: True if subclass serialized, otherwise False
        :rtype: bool
        """
        return os.path.exists(self.serial) and \
            os.stat(self.serial).st_size > 0

    def serialize(self):
        """ Serializes the subclass to system path `serial`.
        """
        self.log.debug(
            'serializing `{}` to `{}` ...'.format(
                self.serialname,
                self.serial
            )
        )
        pickle.dump(self, open(self.serial, 'wb'))

    def deserialize(self):
        """ Deserializes the subclass from system path `serial`.
        """
        self.log.debug(
            'deserializing `{}` from `{}` ...'.format(
                self.serialname,
                self.serial
            )
        )
        setattr(
            self, '__dict__',
            pickle.load(open(self.serial, 'rb')).__dict__
        )

    def serialhandler(self):
        """ Used as the last step of the subclasses __init__ for serialization.
        """
        if not self.serialized():
            self.serialize()
        self.deserialize()
