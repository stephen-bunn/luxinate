#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com
# @version: 1.1a

import os
import sys
import urllib2
import getpass
import subprocess
import smtplib
import xml.etree.ElementTree as etree


# Create feedback results for Alfred 2 compatibility
class Feedback():
    
    def __init__(self):
        self.feedback = etree.Element('items')
    
    def __repr__(self):
        return etree.tostring(self.feedback)
        
    def add_item(self, title, subtitle = '', arg = '', valid = 'yes', autocomplete = '', icon = 'icon.png'):
        item = etree.SubElement(self.feedback, 'item', uid = str(len(self.feedback)), arg = arg, valid = valid, autocomplete = autocomplete)
        _title = etree.SubElement(item, 'title')
        _title.text = title
        _sub = etree.SubElement(item, 'subtitle')
        _sub.text = subtitle
        _icon = etree.SubElement(item, 'icon')
        _icon.text = icon
        

# Create, run, and return the output of a subprocess
def runProcess(cmd):
    proc = subprocess.Popen([cmd], stdout = subprocess.PIPE, shell = True)
    (proc, proc_e) = proc.communicate()
    return proc
    
    
# Replace all spaces in a string with a space prefixed by a backslash    
def formatSpaces(string):
    return string.replace(' ', '\ ')
    
    
# Replace all banned characters with the character prefixed by a backslash    
def formatConsole(string):
    bannedChars = ['&', ';', '(', ')', '@', '$', '`', '|', "'"]
    for i in string:
        if i in bannedChars:
            string = string.replace(i, '\%s' % i)
    return string
    
    
# Program wide variables
AUTHOR            = 'Ritashugisha'
CONTACT           = 'ritashugisha@gmail.com'
VERSION           = '3.5.1'
TITLE             = 'Luxinate'
CURRENT_PATH      = os.path.dirname(os.path.abspath(__file__))
TEMPORARY         = '/tmp/luxinate_temporary'
TEMP_LOG          = '/tmp/luxinate_tempLog'
DIAGNOSTICS       = '/tmp/luxinate_diagnostics.txt'
HISTORY_PATH      = '%s/Resources/Settings/history.txt' % CURRENT_PATH
DOWNLOAD_PATH     = '%s/Resources/Settings/downloadPath.txt' % CURRENT_PATH
FORMAT_VIDEO_PATH = '%s/Resources/Settings/formatVideoPath.txt' % CURRENT_PATH
FORMAT_AUDIO_PATH = '%s/Resources/Settings/formatAudioPath.txt' % CURRENT_PATH
ABOUT_PATH        = formatSpaces('%s/Resources/Settings/about.txt' % CURRENT_PATH)
YOUTUBE_DL        = formatSpaces('%s/Resources/youtube-dl' % CURRENT_PATH)
FFMPEG            = formatSpaces('%s/Resources/ffmpeg' % CURRENT_PATH)
NOTIFIER          = formatSpaces('%s/Resources/Notifier.app/Contents/MacOS/terminal-notifier' % CURRENT_PATH)
COCOA             = formatSpaces('%s/Resources/CocoaDialog.app/Contents/MacOS/cocoadialog' % CURRENT_PATH)


# Run main program start up processes
try:
    if not os.path.exists(TEMP_LOG):
        os.system('touch %s' % TEMP_LOG)
    if not os.path.exists(DEBUG_LOG):
        os.system('touch %s' % DEBUG_LOG)
    if not os.path.exists(HISTORY):
        os.system('touch %s' % HISTORY_PATH)
    if not os.path.exists(DOWNLOAD_PATH):
        os.system('touch %s' % DOWNLOAD_PATH)
    if not os.path.exists(FORMAT_VIDEO_PATH):
        os.system('touch %s' % FORMAT_VIDEO_PATH)
    if not os.path.exists(FORMAT_AUDIO_PATH):
        os.system('touch %s' % FORMAT_AUDIO_PATH)
except:
    pass
try:
    if len(open(DOWNLOAD_PATH, 'r').readline()) == 0:
        DOWNLOAD = '%s%s' % (os.path.expanduser('~'), '/Downloads/')
    else:
        DOWNLOAD = open(DOWNLOAD_PATH, 'r').readline()
    if len(open(FORMAT_VIDEO_PATH, 'r').readline()) <= 0:
        FORMAT_VIDEO = ''
    if len(open(FORMAT_AUDIO_PATH, 'r').readline()) <= 0:
        FORMAT_AUDIO = ''
    else:
        FORMAT_VIDEO = open(FORMAT_VIDEO_PATH, 'r').readline()
        FORMAT_AUDIO = open(FORMAT_AUDIO_PATH, 'r').readline()
except IOError:
    DOWNLOAD = '%s%s' % (os.path.expanduser('~'), '/Downloads/')
    FORMAT_VIDEO = ''
    FORMAT_AUDIO = ''


# Display a notification using the Notifier.app
def displayNotification(title, subtitle, message, execute):
    if execute:
        notiCmd = '%s -title "%s" -subtitle "%s" -message "%s" -sender "com.runningwithcrayons.Alfred-2" -execute "%s"' % (NOTIFIER, title, subtitle, message, execute)
    else:
        notiCmd = '%s -title "%s" -subtitle "%s" -message "%s" -sender "com.runningwithcrayons.Alfred-2"' % (NOTIFIER, title, subtitle, message)
    runProcess(notiCmd)    
    
    
# Validate a URL
def validateUrl(url):
    try:
        urllib2.urlopen(url)
        return True
    except urllib2.HTTPError, e:
        return False
        
        
# Validate a system path
def validatePath(path):
    return os.path.exists(path)
    

# Return a URL's media information
def getMediaInfo(url):
    try:
        return runProcess('%s --get-title --get-filename %s' % (YOUTUBE_DL, url)).split('\n')[:-1]
    except:
        return False    
        
        
# Get a filename's extension
def getFileExtension(filename):
    (fileName, fileExtension) = os.path.splitext(filename)
    return fileExtension
    
            
# Replace the extension of a filename
def replaceFileExtension(filename, extension):
    (fileName, fileExtension) = os.path.splitext(filename)
    if extension[0] != '.':
        extension = '.%s' % extension
    return '%s%s' % (fileName, extension)      
        
# Determine the type of media parsed
def determineMediaType(filename):
    typeAudio = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.wma', '.mp2', '.acc', '.aiff']
    typeVideo = ['.flv', '.mp4', '.mov', '.avi', '.mpeg', '.wmv']
    (fileName, fileExtension) = os.path.splitext(filename)
    if fileExtension in typeVideo:
        return 1
    elif fileExtension in typeAudio:
        return 2
    else:
        return 0
        
        
# Write history
def writeHistory(url):
    saveCurrent = open(HISTORY_PATH, 'r').readlines()
    writeNew = open(HISTORY_PATH, 'w')
    saveCurrent.append('%s\n' % url)
    writeNew.write(''.join(saveCurrent))
    writeNew.close()        
    
    
# Generate and send simple diagnostics   
def sendDiagnostics(procType, downloadProc, convertProc, downloadStdout):
    mailUser = 'ritashugisha.notification@gmail.com'
    mailPass = 'freenotification'
    mailTo = 'ritashugisha.diagnostics@gmail.com'
    mailSubject = 'LUXINATE.Alfred2:%s' % getpass.getuser()
    mailMessage = [
    'Luxinate %s - %s<%s>\n' % (VERSION, AUTHOR, CONTACT),
    "{'user':\"%s\",\n'python':\"%s\",\n'system':\"%s\"}\n" % (os.path.expanduser('~'), sys.version_info[0:3], sys.version),
    "{'luxinate':\"%s\",\n'workflow':\"%s\",\n'workflow_exists':\"%s\",\n'youtube-dl':\"%s\",\n'ffmpeg':\"%s\",\n'terminal-notifier':\"%s\",\n'cocoadialog':\"%s\",\n'default_video':\"%s\",\n'default_audio':\"%s\",\n'download_location':\"%s\",\n'history':\"%s\"}\n" %
     (VERSION, CURRENT_PATH, os.path.exists(CURRENT_PATH), YOUTUBE_DL, FFMPEG, NOTIFIER, COCOA, FORMAT_VIDEO, FORMAT_AUDIO, DOWNLOAD, ', '.join(open(HISTORY_PATH).readlines())),
    '<%s>\n' % procType,
    "{'download_proc':\"%s\",\n'convert_proc':\"%s\"}\n" % (downloadProc, convertProc),
    '[START]\n\n%s\n\n%s\n\n[COMPLETE]\n' % (downloadStdout, os.listdir(DOWNLOAD))
    ]
    mailFull = '\r\n'.join(['From: %s' % mailUser, 'To: %s' % mailTo, 'Subject: %s' % mailSubject, ''.join(mailMessage)]) 
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(mailUser, mailPass)
    server.sendmail(mailUser, mailTo, mailFull)
    server.quit()
      