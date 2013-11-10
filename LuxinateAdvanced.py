#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com
# @version: 1.1a

import os
import utils

# Return available download formats
def getVideoFormats(query):
    videoProcCmd = '%s -F %s' % (utils.YOUTUBE_DL, query)
    videoProc = utils.runProcess(videoProcCmd)
    formatDict = {}
    formatValues = []
    for i in videoProc.split('\n'):
        if '[youtube]' in i.lower() or 'available' in i.lower():
            pass
        else:
            try:
                formatDict[i.replace('\t', '').split(':')[0]] = i.replace('\t', '').split(':')[1].replace('[', ' [')
            except IndexError:
                pass
    for i in formatDict.iteritems():
        formatValues.append(i)
    return formatValues
    

# Advanced download video
def advancedDownloadVideo(node, query, extension, filename, mediaTitle, extraOption):
    savePath = '%s%s' % (utils.DOWNLOADS, utils.formatConsole(utils.formatSpaces(filename)))
    downloadVideoCmd = ('%s -f %s %s -o %s' % (utils.YOUTUBE_DL, extraOption, query, savePath)).replace('\n', '')
    if not utils.validatePath(utils.DOWNLOADS):
        os.system('mkdir %s' % utils.DOWNLOADS)
    utils.writeHistory(query)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOADS)
    utils.runProcess(downloadVideoCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOADS)
    

# Advanced download audio    
def advancedDownloadAudio(node, query, extension, filename, mediaTitle, extraOption):
    savePath = '%s%s' % (utils.DOWNLOADS, utils.formatConsole(utils.formatSpaces(utils.replaceExtension(filename, extension))))
    downloadAudioCmd = ('%s %s -o %s' % (utils.YOUTUBE_DL, query, utils.TEMPORARY)).replace('\n', '')
    if extension == '.mp3':
        convertAudioCmd = ('%s -i %s -b:a 320k %s' % (utils.FFMPEG, utils.TEMPORARY, savePath)).replace('\n', '')
    else:
        convertAudioCmd = ('%s -i %s %s' % (utils.FFMPEG, utils.TEMPORARY, savePath)).replace('\n', '')
    if not utils.validatePath(utils.DOWNLOADS):
        os.system('mkdir %s' % utils.DOWNLOADS)
    utils.writeHistory(query)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOADS)
    utils.runProcess(downloadAudioCmd)
    utils.runProcess(convertAudioCmd)
    os.system('rm -rf %s' % utils.TEMPORARY)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOADS)
        