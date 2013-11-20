#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import os
import utils

def process():
    import ast
    q = ast.literal_eval(open(utils.TEMPFILE, 'r').readlines()[0])
    feed = utils.Feedback()
    if q['node'] == 1:
        for i in getVideoFormats(q['url']):
            feed.add_item(i[1], q['title'], 
            "{'node':%s,'url':'%s','title':'%s','file':'%s','extension':'%s','extra_option':'%s'}" % ('1',
             q['url'], q['title'], q['file'], utils.getExtension(q['file']), i[0]), '', '', 'Icons/_download.png')
        audioFormats = ['.mp3', '.wav', '.m4a', '.ogg', '.wma', '.mp2', '.acc', '.aiff']
        for i in audioFormats:
            feed.add_item(i, q['title'], 
            "{'node':%s,'url':'%s','title':'%s','file':'%s','extension':'%s', 'extra_option':''}" % ('2',
            q['url'], q['title'], q['file'], i), '', '', 'Icons/_download.png')
    elif q['node'] == 2:
        audioFormats = ['.mp3', '.wav', '.m4a', '.ogg', '.wma', '.mp2', '.acc', '.aiff']
        for i in audioFormats:
            feed.add_item(i, q['title'], 
            "{'node':%s,'url':'%s','title':'%s','file':'%s','extension':'%s', 'extra_option':''}" % ('2',
             q['url'], q['title'], q['file'], i), '', '', 'Icons/_download.png')
    elif q['node'] == 3:
        feed.add_item('No Download', 'Not a feature of Advanced Luxinate', '', '', '', 'Icons/_x.png')
    else:
        feed.add_item('Invalid URL', 'Not a feature of Adcanced Luxinate', '', '', '', 'Icons/_x.png')
    print feed

def getVideoFormats(url):
    formatCmd = '%s -F %s' % (utils.YOUTUBE_DL, url)
    format = utils.runProcess(formatCmd)
    formatDict = {}
    formatValues = []
    for i in format.split('\n'):
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
    
def advancedDownloadVideo(node, url, extension, fileName, mediaTitle, format):
    utils.writeHistory(url)
    downloadCmd = 'cd %s;%s -f %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, format, url)
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Video', 'open %s' % utils.DOWNLOAD)
    proc = utils.runProcess(downloadCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('advancedDownloadVideo', downloadCmd, '', proc)
    
def advancedDownloadAudio(node, url, extension, fileName, mediaTitle, format):
    utils.writeHistory(url)
    downloadCmd = '%s %s -o %s' % (utils.YOUTUBE_DL, url, utils.TEMPORARY)
    if extension == '.mp3':
        convertCmd = '%s -i %s -b:a 320k %s' % (utils.FFMPEG, 
        utils.TEMPORARY, '%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(utils.replaceExtension(fileName, extension)))))
    else:
        convertCmd = '%s -i %s %s' % (utils.FFMPEG,
        utils.TEMPORARY, '%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(utils.replaceExtension(fileName, extension)))))
    utils.displayNotification(utils.TITLE, mediaTitle, '► Downloading Audio', 'open %s' % utils.DOWNLOAD)
    proc = utils.runProcess(downloadCmd)
    utils.runProcess(convertCmd)
    utils.displayNotification(utils.TITLE, mediaTitle, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('advancedDownloadAudio', downloadCmd, convertCmd, proc)
