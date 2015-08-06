#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
convert

.. module:: convert
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

import os
import re
import time
import datetime
import tempfile
import subprocess

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess
from settings import Settings
from resource import FFMpegResource


class Converter(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):

    def __init__(self):
        self.ffmpeg = FFMpegResource().resource
        self.settings = Settings().settings

    def __getstate__(self):
        return {
            'ffmpeg': self.ffmpeg
        }

    def convert(self, mod, progress_bar=None):
        self.log.info('applying conversion to {mod}'.format(mod=mod))
        retn = []
        cmd = [
            self.ffmpeg,
            '-i', '{orig}',
            '-vn',
            '-ab', self.settings['audio_bitrate'],
            '{new}'
        ]
        for i in mod.convertable:
            new = '{origbase}.{ext}'.format(
                origbase=os.path.splitext(i)[0],
                ext=self.settings['audio_format']
            )
            cmd = [j.format(orig=i, new=new) for j in cmd]
            if progress_bar:
                progress_bar.update(
                    percent=0,
                    text='Preparing convert...'
                )
            tempprog = os.path.realpath(
                tempfile.mkstemp(prefix='ffmpeg-', suffix='.prog')[1]
            )
            proc = subprocess.Popen(
                cmd,
                stdout=open(tempprog, 'wb'),
                stderr=open(tempprog, 'wb')
            )
            if progress_bar:
                (pos, line, duration, current,) = (None,) * 4
                with open(tempprog, 'r+') as prog:
                    while True:
                        (pos, line,) = (prog.tell(), prog.readline(),)
                        if not line:
                            time.sleep(
                                self._global.ffmpeg_progress_read_time_buffer
                            )
                            prog.seek(pos)
                        else:
                            line = line.strip()
                            (duration_find, current_find, ending_find,) = (
                                re.findall(
                                    self._global.ffmpeg_duration_regex,
                                    line
                                ),
                                re.findall(
                                    self._global.ffmpeg_current_regex,
                                    line
                                ),
                                re.findall(
                                    self._global.ffmpeg_ending_regex,
                                    line
                                )
                            )
                            if duration_find:
                                duration = time.strptime(
                                    duration_find[0].split(
                                        ': '
                                    )[1].split('.')[0],
                                    '%H:%M:%S'
                                )
                                duration = datetime.timedelta(
                                    hours=duration.tm_hour,
                                    minutes=duration.tm_min,
                                    seconds=duration.tm_sec
                                ).total_seconds()
                            elif current_find:
                                current = time.strptime(
                                    current_find[0].split(
                                        '='
                                    )[1].split('.')[0],
                                    '%H:%M:%S'
                                )
                                current = datetime.timedelta(
                                    hours=current.tm_hour,
                                    minutes=current.tm_min,
                                    seconds=current.tm_sec
                                ).total_seconds()
                                progress_bar.update(
                                    percent=float(current / duration) * 100.0,
                                    text='【Converting】{title}'.format(
                                        title=mod.info['title']
                                    )
                                )
                            elif ending_find:
                                break
            retn.append(new)
        os.remove(tempprog)
        return retn
