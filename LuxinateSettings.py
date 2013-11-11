#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com
# @version: 1.1a

import sys
import utils


# Set where downloads are saved to
def setDownloadPath():
    proc = '%s fileselect --title %s --text %s --select-only-directories --stirng-output --float' % (utils.COCOA, utils.TITLE, utils.formatSpaces('Set where downloads are saved to by default:'))
    result = utils.runProcess(proc)
    if len(result.split('\n')) < 2:
        sys.exit(0)
    else:
        downloadText = open(utils.DOWNLOAD_PATH, 'w')
        downloadText.write('%s/' % result.split('\n')[0])
        downloadText.close()
        utils.displayNotification(utils.TITLE, 'Download path changed', '%s/' % result.split('\n')[0], '')
        
        
# Display download history
def displayHistory():
    proc = '%s textbox --title %s --informative-text %s --text-from-file %s --button1 %s --button2 %s --float' % (utils.COCOA, utils.TITLE, utils.formatSpaces('Luxinate download history:'), utils.formatSpaces(utils.HISTORY_PATH), 'Ok', utils.formatSpaces('Clear History'))        
    results = utils.runProcess(proc)
    if results.split('\n')[0] == '2':
        wipeHistory = open(utils.HISTORY_PATH, 'w')
        wipeHistory.close()
        utils.displayNotification(utils.TITLE, 'Luxinate History Cleared', '', '')


# Display about Luxinate
def displayAbout():
    proc = '%s textbox --title %s --informative-text %s --text-from-file %s --button1 %s --float' % (utils.COCOA, utils.TITLE, utils.formatSpaces('About Luxinate:'), utils.ABOUT_PATH, 'Ok')
    utils.runProcess(proc)
    
    
# Set desired video format
def setDesiredVideoFormat():
    currentFormats = {'5':'FLV 240p', '6':'FLV 270p', '17':'3GP 144p', '18':'MP4 360p', '22':'MP4 720p', '34':'FLV 360p',
    '35':'FLV 480p', '36':'3GP 240p', '37':'MP4 1080p', '43':'WebM 360p', '44':'WebM 480p', '45':'WebM 720p', '46':'WebM 1080p',
    '82':'[3D] MP4 360p', '83':'[3D] MP4 240p', '84':'[3D] MP4 720p', '85':'[3D] MP4 520p', '100':'[3D] WebM 360p', '102':'[3D] WebM 720p'}
    currentFormatsList = '"%s"' % '" "'.join(currentFormats.values())
    procCmd = '%s dropdown --title %s --text %s --items %s --string-output --button1 %s --button2 %s --button3 %s --float' % (utils.COCOA, utils.formatSpaces(utils.TITLE), utils.formatSpaces('Choose desired video format:'), currentFormatsList, 'Ok', 'Cancel', 'Reset')    
    desiredFormat = utils.runProcess(procCmd)
    if desiredFormat.split('\n')[0].lower() == 'cancel':
        sys.exit(0)
    elif desiredFormat.split('\n')[0].lower() == 'reset':
        wipeFormat = open(utils.FORMAT_VIDEO_PATH, 'w')
        wipeFormat.close()
        utils.displayNotification(utils.TITLE, 'Default video download format reset', '', '')
    else:
        for key, value in currentFormats.iteritems():
            if value == desiredFormat.split('\n')[1].replace('\n', ''):
                newFormat = open(utils.FORMAT_VIDEO_PATH, 'w')
                newFormat.write(key)
                newFormat.close()
                utils.displayNotification(utils.TITLE, 'Default video format: %s' % value, '', '')

# Set desired audio format
def setDesiredAudioFormat():
    currentFormats = {'.mp3':'MP3', '.wav':'WAV', '.ogg':'OGG', '.m4a':'M4A', '.wma':'WMA'}
    currentFormatsList = '"%s"' % '" "'.join(currentFormats.values())
    procCmd = '%s dropdown --title %s --text %s --items %s --string-output --button1 %s --button2 %s --button3 %s --float' % (utils.COCOA, utils.formatSpaces(utils.TITLE), utils.formatSpaces('Choose default audio format:'), currentFormatsList, 'Ok', 'Cancel', 'Reset')    
    desiredFormat = utils.runProcess(procCmd)
    if desiredFormat.split('\n')[0].lower() == 'cancel':
        sys.exit(0)
    elif desiredFormat.split('\n')[0].lower() == 'reset':
        wipeFormat = open(utils.FORMAT_AUDIO_PATH, 'w')
        wipeFormat.close()
        utils.displayNotification(utils.TITLE, 'Default audio download format reset', '', '')
    else:
        for key, value in currentFormats.iteritems():
            if value == desiredFormat.split('\n')[1].replace('\n', ''):
                newFormat = open(utils.FORMAT_AUDIO_PATH, 'w')
                newFormat.write(key)
                newFormat.close()
                utils.displayNotification(utils.TITLE, 'Default audio format: %s' % value, '', '')
   
# Check for updates by reading the update.txt github       
def checkUpdates():
    import ast
    import urllib2
    import webbrowser
    updateInfo = ast.literal_eval(urllib2.urlopen('https://raw.github.com/Ritashugisha/luxinate/master/Updates/update.txt').read())
    if updateInfo['version'] > utils.VERSION:
        updateCmd = '%s msgbox --title %s --text %s --informative-text %s  --button1 %s --button2 %s --button3 %s --string-output --float' % (utils.COCOA, utils.formatSpaces(utils.TITLE), utils.formatSpaces('Luxinate %s is available to update!' % updateInfo['version']), utils.formatSpaces('Choose which color of Luxinate you would like to update:'), 'Black', 'White', 'Cancel')
        updateResponse = utils.runProcess(updateCmd)
        if updateResponse.lower() == 'cancel':
            sys.exit(0)
        else:
            if updateResponse.lower()[0] == 'w':
                webbrowser.open(updateInfo['white'])
            elif updateResponse.lower()[0] == 'b':
                webbrowser.open(updateInfo['black'])
    else:
        updateCmd = '%s msgbox --title %s --text %s --button1 %s' % (utils.COCOA, utils.formatSpaces(utils.TITLE), utils.formatSpaces('Your version of Luxinate is up to date!'), 'Ok')
        utils.runProcess(updateCmd)
        