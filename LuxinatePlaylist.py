#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import os
import utils

# Validate query URL and format Alfred feed
#
# @param query URL to be validated and passed as next {query}
def process(query):
    feed = utils.Feedback()
    try:
        if utils.validateUrl(query) and 'playlist?list' in query:
            feed.add_item('Download Playlist Video', query, "{'node':%s,'url':\'%s\'}" % ('1', query), '', '', 'Icons/_playlist.png')
            feed.add_item('Download Playlist Audio', query, "{'node':%s, 'url':\'%s\'}" % ('2', query), '', '', 'Icons/_playlist.png')
        else:
            feed.add_item('No Download', 'Invalid playlist URL', '', '', '', 'Icons/_x.png')
    except ValueError:
        feed.add_item('Invalid URL', 'No playlist could be found at %s' % query, '', '', '', 'Icons/_x.png')
    print feed

# Download each video in the validated playlist URL
#
# @param url URL to playlist
def downloadPlaylistVideo(url):
    utils.writeHistory(url)
    if utils.FORMAT_VIDEO:
        downloadCmd = 'cd %s;%s -citf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    utils.displayNotification(utils.TITLE, url, '► Downloading Playlist\'s Video', 'open %s' % utils.DOWNLOAD)    
    proc = utils.runProcess(downloadCmd)
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadPlaylistVideo', downloadCmd, '', proc)

# Download each audio in the validated playlist URL
#
# @param url URL to playlist    
def downloadPlaylistAudio(url):
    utils.writeHistory(url)
    downloadCmd = 'mkdir %s;cd %s;%s -cit %s' % (utils.TEMPDIR, utils.TEMPDIR, utils.YOUTUBE_DL, url)
    utils.displayNotification(utils.TITLE, url, '► Downloading Playlist\'s Audio', 'open %s' % utils.DOWNLOAD)
    proc = utils.runProcess(downloadCmd)
    for i in os.listdir(utils.TEMPDIR):
        if utils.FORMAT_AUDIO:
            if utils.FORMAT_AUDIO == '.mp3':
                convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces('%s%s' % (utils.TEMPDIR, i)),
                utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
            else:
                convertCmd = '%s -i %s %s' % (utils.FFMPEG, utils.formatSpaces('%s%s' % (utils.TEMPDIR, i)),
                utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
        else:
            convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces('%s%s' % (utils.TEMPDIR, i)),
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
        utils.runProcess(convertCmd)
    os.system('rm -rf %s' % utils.TEMPDIR)
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadPlaylistAudio', downloadCmd, convertCmd, proc)
    