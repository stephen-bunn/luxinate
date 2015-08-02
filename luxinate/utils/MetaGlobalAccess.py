#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
MetaGlobalAccess

.. module:: MetaGlobalAccess
    :platform: Linux, MacOSX, Windows
    :synopsis: Gives subclasses access to the __prgm__.Globals through _global.
    :created:  2015-06-10 15:33:36
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

try:
    import __prgm__
except ImportError:
    from .. import __prgm__


class GlobalAccess(object):
    """ Allows subclasses to access the __prgm__.Globals through _global.

    This superclass adds the attribute `_global` to it's subclasses as an
    instance of the __prgm__.Globals class.

    """

    @property
    def _global(self):
        """ The `_global` (__prgm__.Globals) property.
        """
        return __prgm__.Globals()
