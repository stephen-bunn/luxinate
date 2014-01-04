#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com
#
# This file is part of Luxinate.
#
# Luxinate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Luxinate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Luxinate. If not, see <http://www.gnu.org/licenses/>.

import utils, soundcloud

# Search and format tracks on SoundCloud for Alfred 2
#
# @param query Query to search in SoundCloud
def process(query):
    def toString(seconds):
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        seconds = seconds % 3600 % 60
        result = ''
        if hours > 0:
            result = '%sh' % hours
        if minutes > 0:
            if hours > 0:
                result = '%s ' % results
            result = '%s%sm' % (result, minutes)
        if seconds > 0:
            if hours > 0 and minutes == 0 or minutes > 0:
                result = '%s ' % result
            result = '%s%ss' % (result, seconds)
        return result
    client = soundcloud.Client(client_id = utils.SOUNDCLOUD_API)
    f = utils.Feedback()
    tracks = client.get('/tracks', q = query, limit = 9)
    if not tracks:
        f.add_item('No results', 'No results were found', '', '', '', 'Icons/_x.png')
    else:
        for i in tracks:
            f.add_item(i.title, 'by %s [%s]' % (i.user['username'], toString(i.duration / 1000)), i.permalink_url, '', '', 'Icons/_download.png')
    print f
        