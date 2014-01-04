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

import utils

# Use osascript to search either Safari or Chrome for all currently opened tabs
#
# @param browser ('Safari' or 'Chrome')
# @return [URL0, URL1, URL2]
def process(browser):
    osaCmd = "osascript -e 'tell application \"%s\" to get URL of every Tab of every Window'" % browser
    return utils.runProcess(osaCmd).replace('\n', '').split(', ')

# Get open tabs, validate for download, add item to Alfred feed
#
# @param query '{query}' (null)
# @param browser ('Safari' or 'Chrome')
def LuxinateBrowser(query, browser):
    feed = utils.Feedback()
    for i in process(browser):
        try:
            (mediaTitle, mediaFile) = utils.getMediaInfo(i)
            if utils.determineMediaType(mediaFile) == 1:
                q = "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('1',
                i, utils.formatDict(mediaTitle), utils.formatDict(mediaFile))
                feed.add_item(mediaTitle, i, q, '', '', 'Icons/_download.png')
            elif utils.determineMediaType(mediaFile) == 2:
                q = "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('2',
                i, utils.formatDict(mediaTitle), utils.formatDict(mediaFile))
                feed.add_item(mediaTitle, i, q, '', '', 'Icons/_download.png')
        except ValueError:
            feed.add_item('No download', 'Invalid URL %s' % i, "{'node':%s}" % '0', '', '', 'Icons/_x.png')
    print feed

# Tell application Alfred 2 to search for the default lux option and pass the selected URL
#
# @param query Dictionary of download information    
def openLuxDefault(query):
    osaCmd = 'osascript -e \'tell application "Alfred 2" to search "luxinate ► " & "' + query['url'] + '"\''
    utils.runProcess(osaCmd)
    