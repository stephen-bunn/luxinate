#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import os
import utils

# Filter dictionary query to specific node download
#
# @param query Dictionary of download information
def runFilter(query):
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
    if utils.FORMAT_VIDEO:
        downloadCmd = 'cd %s;%s -itf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
    proc = utils.runProcess(downloadCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadVideo', downloadCmd, '', proc)

# Download the audio located at URL
#
# @param url URL to be downloaded from    
def downloadAudio(url):
    utils.writeHistory(url)
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    downloadCmd = '%s -i %s -o %s' % (utils.YOUTUBE_DL, url, utils.TEMPORARY)
    if utils.FORMAT_AUDIO:
        if utils.FORMAT_AUDIO == '.mp3':
            convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.TEMPORARY, 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
        else:
            convertCmd = '%s -i %s %s' % (utils.FFMPEG, utils.TEMPORARY, 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
    else:
        convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.TEMPORARY, 
        utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
    proc = utils.runProcess(downloadCmd)
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
    if utils.FORMAT_VIDEO:
        downloadCmd = 'cd %s;%s -itf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.FORMAT_AUDIO:
        if utils.FORMAT_AUDIO == '.mp3':
            convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatConsole('%s%s' % (utils.DOWNLOAD, mediaFile)), 
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
        else:
            convertCmd = '%s -i %s %s' % (utils.FFMPEG, utils.formatConsole('%s%s' % (utils.DOWNLOAD, mediaFile)),
            utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
    else:
        convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatConsole('%s%s' % (utils.DOWNLOAD, mediaFile)), 
        utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
    proc = utils.runProcess(downloadCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
    utils.runProcess(convertCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadVideo_Audio', downloadCmd, convertCmd, proc)
    