#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com
# @version: 1.1a

import os
import utils


# Download a playlist's video
def downloadPlaylistVideo(url):
    if not utils.validatePath(utils.DOWNLOAD):
        os.system('mkdir %s' % utils.DOWNLOAD)
    utils.writeHistory(url)
    utils.displayNotification(utils.TITLE, url, '► Downloading Playlist\'s Video', 'open %s' % utils.DOWNLOAD)
    if utils.FORMAT_VIDEO:
        proc = 'cd %s;%s -citf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        proc = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    utils.runProcess(proc)
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)


# Download a playlist's audio
def downloadPlaylistAudio(url):
    if not utils.validatePath(utils.DOWNLOAD):
        os.system('mkdir %s' % utils.DOWNLOAD)
    utils.writeHistory(url)
    utils.displayNotification(utils.TITLE, url, '► Downloading Playlist\'s Audio', 'open %s' % utils.DOWNLOAD)
    downloadProc = 'mkdir /tmp/temp_hold/;cd /tmp/temp_hold/;%s -cit %s' % (utils.YOUTUBE_DL, url)
    utils.runProcess(downloadProc)
    for i in os.listdir('/tmp/temp_hold'):
        if utils.FORMAT_AUDIO:
            convertProc = '%s -i %s %s' % (utils.FFMPEG, utils.formatSpaces('/tmp/temp_hold/%s' % i), utils.replaceFileExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
        else:
            convertProc = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces('/tmp/temp_hold/%s' % i), utils.replaceFileExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(i))), '.mp3'))
        utils.runProcess(convertProc)
    os.system('rm -rf /tmp/temp_hold/')
    utils.displayNotification(utils.TITLE, url, 'Downlaod Complete', 'open %s' % utils.DOWNLOAD)
    