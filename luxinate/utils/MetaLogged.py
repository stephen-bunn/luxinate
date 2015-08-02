#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
MetaLogged

.. module:: MetaLogged
    :platform: Linux, MacOSX, Windows
    :synopsis: Adds a logging object to subclasses (non-portable).
    :created:  2015-06-10 15:28:29
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

import logging
import logging.handlers

import MetaGlobalAccess


class Logged(MetaGlobalAccess.GlobalAccess, object):
    """ Adds a logging.Logger attribute to it's subclasses through log.

    This superclass adds an attribute `log` to it's subclasses as an instance
    of the logging.Logger class. This class depends on access to the
    MetaGlobalAccess.GlobalAccess superclass as well as several attributes
    found within the __prgm__.Globals class.

    .. note::
        This class is not portable. Dependencies follow below:
            - MetaGlobalAccess.GlobalAccess
            - __prgm__.Globals
            - __prgm__.Globals -> log_path
            - __prgm__.Globals -> log_size
            - __prgm__.Globals -> log_backup
            - __prgm__.Globals -> log_file_fmt
            - __prgm__.Globals -> log_file_datefmt
            - __prgm__.Globals -> log_console_fmt
            - __prgm__.Globals -> log_console_datefmt
            - __prgm__.Globals -> log_level

    """

    @property
    def log(self):
        """ The `log` (logging.Logger) property.
        """
        return self._global.log
        # NOTE: Since the main logging is handled by AB, we dont need to define
        #
        # logger = logging.getLogger(self.__class__.__name__)
        # if not logger.handlers:
        #
        #     assert hasattr(self._global, 'log_console_fmt'), \
        #         'log requires at least global attribute `log_console_fmt`'
        #
        #     defaults = {
        #         'log_level': logging.DEBUG,
        #         'log_path': None,
        #         'log_size': (1024 * 1024),
        #         'log_backup': 1,
        #         'log_file_fmt': (
        #             '%(asctime)s,%(filename)s,%(lineno)s,'
        #             '%(name)s,%(funcName)s,%(levelname)s,"%(message)s"'
        #         ),
        #         'log_console_datefmt': '%H:%M:%S'
        #     }
        #     for (k, v,) in defaults.iteritems():
        #         if not hasattr(self._global, k):
        #             setattr(self._global, k, v)
        #
        #     # Build the log file handler
        #     if hasattr(self._global, 'log_path') and self._global.log_path:
        #         logfile_handler = logging.handlers.RotatingFileHandler(
        #             self._global.log_path,
        #             maxBytes=self._global.log_size,
        #             backupCount=self._global.log_backup
        #         )
        #         logfile_handler.setFormatter(
        #             logging.Formatter(
        #                 fmt=self._global.log_file_fmt,
        #                 datefmt=self._global.log_file_datefmt
        #             )
        #         )
        #         logger.addHandler(logfile_handler)
        #
        #     # Build the log console handler
        #     console_handler = logging.StreamHandler()
        #     console_handler.setFormatter(
        #         logging.Formatter(
        #             fmt=self._global.log_console_fmt,
        #             datefmt=self._global.log_console_datefmt
        #         )
        #     )
        #     logger.addHandler(console_handler)
        #
        # logger.propogate = False
        # logger.setLevel(self._global.log_level)
        # return logger
