#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
MetaSingleton

.. module:: MetaSingleton
    :platform: Linux, MacOSX, Windows
    :synopsis: Defines a singleton superclass for Python classes.
    :created:  2015-04-25 00:03:13
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""


class Singleton(object):
    """ Defines a Singleton Pattern superclass to be used in immutable objects.

    This object keeps track of the instances created of a specific object
    allowing only one instance of that object to be constructed.
    In the case that there is already one of a specific object already
    instantiated, this class will return that instance instead of creating
    a new instance of that object.

    .. note::
        A singleton object is an object with no methods, simply defined as
        a data sink. For a more indepth analysis on singletons in Python
        read this excellent discussion:
            http://stackoverflow.com/questions/6760685/

    """
    _instances = {}

    def __new__(class_, *args, **kwargs):
        """ Catches an object mid-construction.

        This ensures that only one instance of the given object exists.
        If an instance of the given object already exists, the instance of
        that object is returned as the created object.

        """
        if class_ not in class_._instances:
            class_._instances[class_] = \
                    super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]
