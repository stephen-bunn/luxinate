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

import re, os, ast
import utils

# Get a list of available formats for the passed URL
#
# @param url URL to be analyzed
# @return formatValues [value0, value1, value2, ...]
def getVideoFormats(url):
    formatCmd = '%s -F %s' % (utils.YOUTUBE_DL, url)
    format = utils.runProcess(formatCmd)
    formatDict = {}
    formatValues = []
    for i in format.split('\n'):
        if '[youtube]' in i.lower() or 'available' in i.lower() or 'format code' in i.lower():
            pass
        else:
            try:
                fileFormats = re.sub(' +', ':', i).split(':')
                formatDict[fileFormats[0]] = '%s  [%s]' % (fileFormats[1], fileFormats[2])
            except IndexError:
                pass
    for i in formatDict.iteritems():
        formatValues.append(i)
    return formatValues

# Evaluate the saved dictionary at TEMPFILE and format feed for Alfred 2 accordingly
def process():
    q = ast.literal_eval(utils.deformatConsole(open(utils.TEMPFILE, 'r').readlines()[0]))
    feed = utils.Feedback()
    audioFormats = ['.mp3', '.wav', '.m4a', '.ogg', '.wma', '.mp2', '.acc', '.aiff']
    if q['node'] == 1:
        for i in getVideoFormats(q['url']):
            feed.add_item(i[1], q['title'], 
            "{'node':%s,'url':'%s','title':'%s','file':'%s','extension':'%s','extra_option':'%s'}" % ('1',
             q['url'], q['title'], q['file'], utils.getExtension(q['file']), i[0]), '', '', 'Icons/_download.png')
        for i in audioFormats:
            feed.add_item(i, q['title'], 
            "{'node':%s,'url':'%s','title':'%s','file':'%s','extension':'%s','extra_option':''}" % ('2',
            q['url'], q['title'], q['file'], i), '', '', 'Icons/_download.png')
    elif q['node'] == 2:
        for i in audioFormats:
            feed.add_item(i, q['title'], 
            "{'node':%s,'url':'%s','title':'%s','file':'%s','extension':'%s','extra_option':''}" % ('2',
             q['url'], q['title'], q['file'], i), '', '', 'Icons/_download.png')
    elif q['node'] == 3:
        feed.add_item('No Download', 'Not a feature of Advanced Luxinate', '', '', '', 'Icons/_x.png')
    else:
        feed.add_item('Invalid URL', 'Not a feature of Adcanced Luxinate', '', '', '', 'Icons/_x.png')
    print feed

# Download the video according to the specified parameters
#
# @param node Video node (1)
# @param url URL to be downloaded
# @param extension Extension to be changed (null)
# @param fileName Name of file at URL
# @param mediaTitle Title of URL download
# @oaram format Format value to be passed
def advancedDownloadVideo(node, url, extension, fileName, mediaTitle, format):
    utils.writeHistory(url)
    utils.writeTemp(url)
    downloadCmd = 'cd %s;%s -f %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, format, url)
    if utils.PROGRESS:
        downloadCmd = '%s --newline' % downloadCmd
        proc = utils.runProgressBarDownload(downloadCmd)
    else:
        utils.displayNotification(utils.TITLE, utils.deformatConsole(mediaTitle), '► Downloading Video', 'open %s' % utils.DOWNLOAD)
        proc = utils.runProcess(downloadCmd)
    utils.killProgressBar()
    utils.displayNotification(utils.TITLE, utils.deformatConsole(mediaTitle), 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('advancedDownloadVideo', downloadCmd, '', proc)

# Download the audio according to the specified parameters 
#
# @param node Audio node (2)
# @param url URL to be downloaded
# @param extension Extension to be changed
# @param fileName Name of file at URL
# @param mediaTitle Title of URL downloaded
# @param format Format value to be passed (null)
def advancedDownloadAudio(node, url, extension, fileName, mediaTitle, format):
    utils.writeHistory(url)
    utils.writeTemp(url)     
    downloadCmd = '%s %s -o %s' % (utils.YOUTUBE_DL, url, utils.TEMPORARY)
    if extension == '.mp3':
        convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, 
        utils.TEMPORARY, '%s%s' % (utils.DOWNLOAD, utils.replaceExtension(fileName, extension)))
    else:
        convertCmd = '%s -y -i %s %s' % (utils.FFMPEG,
        utils.TEMPORARY, '%s%s' % (utils.DOWNLOAD, utils.replaceExtension(fileName, extension)))
    if utils.PROGRESS:
        downloadCmd = '%s --newline' % downloadCmd
        utils.runProgressBarDownload(downloadCmd, quitFilter = False)
        proc = ''
        utils.runProgressBarConvert(convertCmd)
    else:
        utils.displayNotification(utils.TITLE, utils.deformatConsole(mediaTitle), '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
        proc = utils.runProcess(downloadCmd)
        utils.runProcess(convertCmd)
    utils.killProgressBar()
    utils.displayNotification(utils.TITLE, utils.deformatConsole(mediaTitle), 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('advancedDownloadAudio', downloadCmd, convertCmd, proc)

# Filter to specified download node
#
# @param query Dictionary string with download information
def parseQuery(query):
    if query['node'] == 1:
        advancedDownloadVideo(query['node'], query['url'], query['extension'], query['file'], query['title'], query['extra_option'])
    else:
        advancedDownloadAudio(query['node'], query['url'], query['extension'], query['file'], query['title'], query['extra_option'])
