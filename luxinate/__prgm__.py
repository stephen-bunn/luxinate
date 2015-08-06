#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
__prgm__

.. module:: __prgm__
    :platform: Linux, MacOSX, Windows
    :synopsis:
    :created:  2015-04-25 00:03:13
    :modified: ritashugisha
.. moduleauthor:: Ritashugisha (ritashugisha@gmail.com)

"""

import os
import re
import sys
import enum
import urllib2
import logging
import platform
import subprocess

from utils import MetaSingleton


class Globals(MetaSingleton.Singleton):

    os.environ['AB_BRANCH'] = 'devel'

    # default system information
    platform = platform.system()
    bit64 = sys.maxsize > 2**32
    bit32 = not bit64

    # default author information
    author_name = 'Ritashugisha'
    author_email = 'ritashugisha@gmail.com'

    # default module information
    module_name = 'Luxinate'
    module_bundle = 'com.{author}.{module}'.format(
        author=author_name.lower(),
        module=module_name.lower()
    )
    module_version = {'major': 8, 'minor': 1, 'revison': 'alpha'}
    module_version_string = '.'.join([str(i) for i in module_version.values()])
    base_path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    base_name = os.path.basename(base_path)
    outer_base_path = os.path.dirname(base_path)

    # dynamic paths (may exist or not), required for valid operation
    storage_path = os.path.join(outer_base_path, 'storage')
    serial_path = os.path.join(storage_path, 'serials')
    workflow_icon = os.path.join(outer_base_path, 'icon.png')

    _dynamic_directories = (
        storage_path,
        serial_path,
    )

    temp_storage_suffix = '-{}'.format(module_name.lower())

    # backend logging setup
    # NOTE: client should handle replacing the global log to AB's logger
    log_level = logging.DEBUG
    log = logging.getLogger('BACKEND')
    _log_handler = logging.StreamHandler()
    _log_handler_fmt = logging.Formatter(
        fmt='[%(name)s.%(levelname)s] %(message)s'
    )
    _log_handler.setFormatter(_log_handler_fmt)
    log.addHandler(_log_handler)
    log.propogate = False
    log.setLevel(log_level)

    # settings defaults
    settings_defaults = {
        'save_to': os.path.join(os.path.expanduser('~'), 'Downloads'),
        'outtmpl': '%(title)s-%(id)s.%(ext)s',
        'progress': True,
        'audio_format': 'mp3',
        'audio_bitrate': '320k'
    }
    settings_options = {
        'audio_format': ['mp3', 'flac', 'ogg'],
        'audio_bitrate': ['128k', '256k', '320k'],
    }

    # history defaults
    history_defaults = {
        'count': 0,
        'items': {}
    }
    history_mod_item_blacklist = ['requested_formats', 'formats']

    # type variable globals
    class MediaType(enum.Enum):
        video = 0xf1
        audio = 0xf2

    class DownloadType(enum.Enum):
        video = 0x01
        audio = 0x02
        combi = 0x04

    class ConvertType(enum.Enum):
        video2audio = 0x11
        audio2audio = 0x12

    # converter variable globals
    ffmpeg_binary_host = 'http://ffmpegmac.net/'
    ffmpeg_progress_read_time_buffer = 0.05
    ffmpeg_progress_exit_time_buffer = 1
    ffmpeg_duration_regex = ur'(Duration: [0-9:.]*)'
    ffmpeg_current_regex = ur'(time=[0-9:.]*)'
    ffmpeg_ending_regex = ur'video:(.?)'
    common_audio_exts = [
        '3gp', 'act', 'aiff', 'aac', 'amr', 'ape', 'au', 'awb', 'dct', 'dss',
        'dvf', 'flac', 'gsm', 'iklax', 'ivs', 'm4a', 'm4p', 'mmf', 'mp3',
        'mpc', 'msv', 'ogg', 'oga', 'opus', 'ra', 'rm', 'raw', 'sln', 'tta',
        'vox', 'wav', 'wma', 'wv'
    ]

    # embedder variable globals
    default_comment = 'Downloaded using {}v{} by {}'.format(
        module_name, module_version_string, author_name
    )

    # connection information
    http_test_connection = 'http://www.google.com'
    http_test_timeout = 1
    http_regex = (
        ur'('
        ur'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+\-~#=\u00a1-\uffff]{2,256}'
        ur'\.[a-z]{2,6}|'
        ur'(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}'
        ur'([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
        ur')\b'
        ur'([a-zA-Z0-9@:;%_\.,\(\)\+\-~#?&//=\u00a1-\uffff]*)'
    )

    # required wrappers, built by Client instantiation
    wrappers = {'cd_client': 'cocoadialog', 'tn_client': 'terminalnotifier'}

    # icon dictionary, filled by Client's bundler specifications
    icons = {
        'link-broken': ('open-iconic', 'link-broken', 'ffffff',),
        'unsupported': ('open-iconic', 'ban', 'ffffff',),
        'video': ('open-iconic', 'media-play', 'ffffff',),
        'audio': ('open-iconic', 'audio-spectrum', 'ffffff',),
        'ellipses': ('open-iconic', 'ellipses', 'ffffff',),
        'check': ('open-iconic', 'check', 'ffffff',),
        'x': ('open-iconic', 'x', 'ffffff',),
        'folder': ('open-iconic', 'folder', 'ffffff',),
        'tags': ('open-iconic', 'tags', 'ffffff',),
        'delete': ('open-iconic', 'delete', 'ffffff',),
        'entry': ('open-iconic', 'chevron-right', 'ffffff',),
        'headphones': ('open-iconic', 'headphones', 'ffffff',),
        'musical-note': ('open-iconic', 'musical-note', 'ffffff',),
        'code': ('open-iconic', 'code', 'ffffff',),
    }

    # notification information
    notify_sender = 'com.runningwithcrayons.Alfred-2'
    notify_group = 'com.ritashugsha.{}'.format(module_name.lower())
    notify_sound = 'glass'

    # dialog variable globals
    progressbar_kill_time_buffer = 0.5

    # misc information
    outtmpl_link = (
        "https://github.com/rg3/youtube-dl/blob/master/"
        "README.md#output-template"
    )

    def __init__(self):
        if not self._valid_environment:
            self._setup_environment()

    @property
    def _valid_environment(self):
        return all([
            (os.path.exists(i) and os.path.isdir(i))
            for i in self._dynamic_directories
        ]) and 'darwin' in self.platform.lower()

    def _setup_environment(self):
        for directory in self._dynamic_directories:
            if not os.path.exists(directory) or not os.path.isdir(directory):
                os.makedirs(directory, 0775)

    def _build_icons(self):
        if hasattr(self, 'ab'):
            for (name, args,) in self.icons.iteritems():
                self.icons[name] = self.ab.icon(*args)

    def _build_wrappers(self):
        if hasattr(self, 'ab'):
            for (name, wrapper,) in self.wrappers.iteritems():
                setattr(self, name, self.ab.wrapper(wrapper))

    def _run_subprocess(self, process):
        if isinstance(process, basestring):
            process = [process]
        assert process and isinstance(process, list), \
            'subprocess process must be formatted as list'
        (proc, proc_err,) = subprocess.Popen(
            process,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()
        return proc

    def _merge_dicts(self, *dicts):
        retn = {}
        for i in dicts:
            if isinstance(i, dict):
                retn.update(i)
        return retn

    def _has_connection(self):
        try:
            urllib2.urlopen(
                self.http_test_connection,
                timeout=self.http_test_timeout
            )
            return True
        except urllib2.URLError:
            pass
        return False

    def _match_url(self, url):
        if re.match(self.http_regex, url):
            try:
                urllib2.urlopen(url)
                return True
            except urllib2.URLError:
                pass
        return False

    def _download_type(self, dtype):
        if isinstance(dtype, self.DownloadType):
            return dict([
                (v, k,)
                for (k, v,) in self.DownloadType._value2member_map_.iteritems()
            ])[dtype]
        elif isinstance(dtype, int):
            try:
                return self.DownloadType._value2member_map_[dtype]
            except KeyError:
                self.log.error(
                    'no available download type with value `{}` ...'.format(
                        dtype
                    )
                )
        else:
            self.log.debug(
                'couldn\'t translate download type `{}` ...'.format(dtype)
            )
        return None
