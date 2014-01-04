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

import os
import utils

# Start up process
#
# @param query Initial query
def process(query):
    f = utils.Feedback()
    try:
        (mediaTitle, mediaFile) = utils.getMediaInfo(query)
        if utils.determineMediaType(mediaFile) == 1:
            f.add_item('Download Video', mediaTitle,
                "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('1',
                query, utils.formatDict(mediaTitle), utils.formatDict(mediaFile)), '', '', 'Icons/_video.png')
            f.add_item('Download Audio', mediaTitle, 
                "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('2',
                 query, utils.formatDict(mediaTitle), utils.formatDict(mediaFile)), '', '', 'Icons/_audio.png')
            f.add_item('Download Video and Audio', mediaTitle, 
                "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('3',
                 query, utils.formatDict(mediaTitle), utils.formatDict(mediaFile)), '', '', 'Icons/_both.png')
        elif utils.determineMediaType(mediaFile) == 2:
            f.add_item('Download Audio', mediaTitle, 
                "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('2', query,
                 utils.formatDict(mediaTitle), utils.formatDict(mediaFile)), '', '', 'Icons/_audio.png')
        else:
            pass
    except ValueError:
       f.add_item('Invalid URL', 'No available downloads at %s' % query, '', '', '', 'Icons/_x.png')
    print f

# Filter dictionary query to specific node download
#
# @param query Dictionary of download information
def parseQuery(query):
    if query['node'] == 1:
        downloadVideo(query['url'])
    elif query['node'] == 2:
        downloadAudio(query['url'])
    elif query['node'] == 3:
        downloadVideo_Audio(query['url'])
    else:
        pass

# Download the video located at URL
#
# @param url URL to be downloaded from
def downloadVideo(url):
    utils.writeHistory(url)
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    utils.writeTemp(url)
    if utils.FORMAT_VIDEO:
        downloadCmd = 'cd %s;%s -itf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.PROGRESS:
        downloadCmd = '%s --newline' % downloadCmd
        proc = utils.runProgressBarDownload(downloadCmd)
    else:
        utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
        proc = utils.runProcess(downloadCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadVideo', downloadCmd, '', proc)

# Download the audio located at URL
#
# @param url URL to be downloaded from    
def downloadAudio(url):
    passConvert = False
    utils.writeHistory(url)
    if 'soundcloud' in utils.checkDomain(url):
        passConvert = True
        convertCmd = ''
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    utils.writeTemp(url)
    if not passConvert:
        downloadCmd = '%s -i %s -o %s' % (utils.YOUTUBE_DL, url, utils.TEMPORARY)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.FORMAT_AUDIO:
        if utils.FORMAT_AUDIO == '.mp3':
            convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, utils.TEMPORARY, 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
        else:
            convertCmd = '%s -y -i %s %s' % (utils.FFMPEG, utils.TEMPORARY, 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
    else:
        if not passConvert:
            convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, utils.TEMPORARY, 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
    if utils.PROGRESS:
        downloadCmd = '%s --newline' % downloadCmd
        if not passConvert:
            proc = utils.runProgressBarDownload(downloadCmd, quitFilter = False)
            utils.runProgressBarConvert(convertCmd)
        else:
            proc = utils.runProgressBarDownload(downloadCmd)
    else:
        utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
        proc = utils.runProcess(downloadCmd)
        if not passConvert:
            utils.runProcess(convertCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    os.system('rm -rf %s' % utils.TEMPORARY)
    utils.sendDiagnostics('downloadAudio', downloadCmd, convertCmd, proc)

# Download both the video and audio at URL
#
# @param url URL to be downloaded from    
def downloadVideo_Audio(url):
    utils.writeHistory(url)
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    utils.writeTemp(url)
    if utils.FORMAT_VIDEO:
        downloadCmd = 'cd %s;%s -itf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.FORMAT_AUDIO:
        if utils.FORMAT_AUDIO == '.mp3':
            convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatConsole(utils.formatSpaces('%s%s' % (utils.DOWNLOAD, mediaFile))), 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
        else:
            convertCmd = '%s -y -i %s %s' % (utils.FFMPEG, utils.formatConsole(utils.formatSpaces('%s%s' % (utils.DOWNLOAD, mediaFile))),
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
    else:
        convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatConsole(utils.formatSpaces('%s%s' % (utils.DOWNLOAD, mediaFile))), 
        utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
    if utils.PROGRESS:
        downloadCmd = '%s --newline' % downloadCmd
        proc = utils.runProgressBarDownload(downloadCmd, quitFilter = False)
        utils.runProgressBarConvert(convertCmd)
    else:
        utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
        proc = utils.runProcess(downloadCmd)
        utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
        utils.runProcess(convertCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadVideo_Audio', downloadCmd, convertCmd, proc)
                          