#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com
# @version: 1.1a

import os
import utils


# Download video from url
def downloadVideo(url):
    if not utils.validatePath(utils.DOWNLOAD):
        os.system('mkdir %s' % utils.DOWNLOAD)
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    utils.writeHistory(url)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
    if utils.FORMAT_VIDEO:
        procCmd = 'cd %s;%s -itf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        procCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    proc = utils.runProcess(procCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadVideo', procCmd, '', proc)
    

# Download audio from url
def downloadAudio(url):
    if not utils.validatePath(utils.DOWNLOAD):
        os.system('mkdir %s' % utils.DOWNLOAD)
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    utils.writeHistory(url)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
    downloadProc = '%s -i %s -o %s' % (utils.YOUTUBE_DL, url, utils.TEMPORARY)
    if utils.FORMAT_AUDIO:
        convertProc = '%s -i %s %s' % (utils.FFMPEG, utils.TEMPORARY, utils.replaceFileExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
    else:
        convertProc = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.TEMPORARY, utils.replaceFileExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
    download = utils.runProcess(downloadProc)
    convert = utils.runProcess(convertProc)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    os.system('rm -rf %s' % utils.TEMPORARY)
    utils.sendDiagnostics('downloadAudio', downloadProc, convertProc, download)
    
    
# Download both video and audio from url
def downloadVideo_Audio(url):
    if not utils.validatePath(utils.DOWNLOAD):
        os.system('mkdir %s' % utils.DOWNLOAD)
    (mediaTitle, mediaFile) = utils.getMediaInfo(url)
    utils.writeHistory(url)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
    if utils.FORMAT_VIDEO:
        downloadProc = 'cd %s;%s -itf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT, url)
    else:
        downloadProc = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.FORMAT_AUDIO:
        convertProc = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces(utils.formatConsole('%s%s' % (utils.DOWNLOAD, mediaFile))), utils.replaceFileExtension(utils.formatConsole(utils.formatSpaces('%s%s' % (utils.DOWNLOAD, mediaFile))), utils.FORMAT_AUDIO))
    else:
        convertProc = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces(utils.formatConsole('%s%s' % (utils.DOWNLOAD, mediaFile))), utils.replaceFileExtension(utils.formatConsole(utils.formatSpaces('%s%s' % (utils.DOWNLOAD, mediaFile))), '.mp3'))
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
    download = utils.runProcess(downloadProc)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
    convert = utils.runProcess(convertProc)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadVideo_Audio', downloadProc, convertProc, download)
              
           