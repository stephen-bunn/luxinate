#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import os
import sys
import urllib2
import getpass
import smtplib
import subprocess
import webbrowser
import xml.etree.ElementTree as etree

# Generate feed for Alfred 2 script filters
# feed.add_item(Title, Subtitle, {query}, '', '', Icon path)
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

# Run and return results from a subprocess system command
#
# @param procCmd System command
# @return proc Subprocess.PIPE of procCmd
def runProcess(procCmd):
    proc = subprocess.Popen([procCmd], stdout = subprocess.PIPE, shell = True)
    (proc, proc_e) = proc.communicate()
    return proc

# Replace all spaces with an escape character
#
# @param string String to be formatted
# @return string String with spaces escaped
def formatSpaces(string):
    return string.replace(' ', '\ ')

# Accompany all critical characters with an excape character
#
# @param string String to be formatted
# @return string String with characters escaped
def formatConsole(string):
    formatChars = ['&', ';', '(', ')', '@', '$', '`', '|', "'"]
    for i in formatChars:
        if i in formatChars:
            string = string.replace(i, '\%s' % i)
    return string

# Remove all single and double quotes from a string
#
# @param string String to be formatted
# @return string String without single and double quotes    
def formatDict(string):
    return string.replace('"', '').replace("'", '')

# Global static variables {CRITICAL STATE}
AUTHOR            = 'Ritashugisha'
CONTACT           = 'ritashugisha@gmail.com'
VERSION           = '3.6.1'
TITLE             = 'Luxinate'
CURRENT_PATH      = os.path.dirname(os.path.abspath(__file__))
TEMPORARY         = '/tmp/luxinate_temporary'
TEMPDIR           = '/tmp/luxinate_temporary_directory/'
TEMPFILE          = '/tmp/luxinate_temporary_file'
DIAGNOSTICS       = '/tmp/luxinate_diagnostics.txt'
HISTORY           = '%s/Resources/Settings/history' % CURRENT_PATH
DOWNLOADS         = '%s/Resources/Settings/downloads' % CURRENT_PATH
FORMAT_VIDEO_PATH = '%s/Resources/Settings/formatV' % CURRENT_PATH
FORMAT_AUDIO_PATH = '%s/Resources/Settings/formatA' % CURRENT_PATH
ABOUT             = formatSpaces('%s/Resources/Settings/about' % CURRENT_PATH)
YOUTUBE_DL        = formatSpaces('%s/Resources/youtube-dl' % CURRENT_PATH)
FFMPEG            = formatSpaces('%s/Resources/ffmpeg' % CURRENT_PATH)
NOTIFIER          = formatSpaces('%s/Resources/Notifier.app/Contents/MacOS/terminal-notifier' % CURRENT_PATH)
COCOA             = formatSpaces('%s/Resources/CocoaDialog.app/Contents/MacOS/cocoadialog' % CURRENT_PATH)
SOUNDCLOUD_API    = 'd41555ed08885c41508d9aa7bc9c25b9'

# Run pre-execute processes
# Validate all needed files and directories exists
try:
    if os.path.exists(TEMPORARY):
        os.system('rm -rf %s' % TEMPORARY)
    if not os.path.exists(DIAGNOSTICS):
        os.system('touch %s' % DIAGNOSTICS)
    if not os.path.exists(HISTORY):
        os.system('touch %s' % HISTORY)
    if not os.path.exists(DOWNLOADS):
        os.system('touch %s' % DOWNLOADS)
    if not os.path.exists(FORMAT_VIDEO_PATH):
        os.system('touch %s' % FORMAT_VIDEO_PATH)
    if not os.path.exists(FORMAT_AUDIO_PATH):
        os.system('touch %s' % FORMAT_AUDIO_PATH)
    if not os.path.exists(ABOUT):
        os.system('touch %s' % ABOUT)
    if not os.path.exists(TEMPDIR):
        os.system('mkdir %s' % TEMPDIR)
    if not os.path.exists(TEMPFILE):
        os.system('touch %s' % TEMPFILE)
except:
    pass
# Gather specific custom information for download location and
# default formats for video and audio download
try:
    if len(open(DOWNLOADS, 'r').readline()) == 0:
        DOWNLOAD = formatSpaces('%s%s' % (os.path.expanduser('~'), '/Downloads/'))
    else:
        DOWNLOAD = formatSpaces(open(DOWNLOADS, 'r').readline())
    if len(open(FORMAT_VIDEO_PATH, 'r').readline()) == 0:
        FORMAT_VIDEO = ''
    else:
        FORMAT_VIDEO = open(FORMAT_VIDEO_PATH, 'r').readline()
    if len(open(FORMAT_AUDIO_PATH, 'r').readline()) == 0:
        FORMAT_AUDIO = ''
    else:
        FORMAT_AUDIO = open(FORMAT_AUDIO_PATH, 'r').readline()
except IOError:
    DOWNLOAD = formatSpaces('%s%s' % (os.path.expanduser('~'), '/Downloads/'))
    FORMAT_VIDEO = ''
    FORMAT_AUDIO = ''
# Create download directory if it doesn't exist
if not os.path.exists(DOWNLOAD):
    os.system('mkdir %s' % DOWNLOAD)

# Display a OSX notification
#
# @param title Title of notification
# @param subtitle Subtitle of notification
# @param message Message of notification
# @param execute System command to be executed on click of notification
def displayNotification(title, subtitle, message, execute):
    if execute:
        notifyCmd = '%s -title "%s" -subtitle "%s" -message "%s" -sender "com.runningwithcrayons.Alfred-2" -execute "%s"' % (NOTIFIER, title, subtitle, message, execute)
    else:
        notifyCmd = '%s -title "%s" -subtitle "%s" -message "%s" -sender "com.runningwithcrayons.Alfred-2"' % (NOTIFIER, title, subtitle, message)
    runProcess(notifyCmd)

# Validate any URL passed
#
# @param url URL to be validated
# @return boolean True if valid, otherwise False   
def validateUrl(url):
    try:
        urllib2.urlopen(url)
        return True
    except urllib2.HTTPError, e:
        return False

# Get the title and filename of the valid URL passed
#
# @param url Valid URL to gather information from
# @return [Title, FileName]        
def getMediaInfo(url):
    try:
        return runProcess('%s --get-title --get-filename %s' % (YOUTUBE_DL, url)).split('\n')[:-1]
    except:
        return False

# Get the extension of the filename passed
#
# @param filename File name including extension
# @return fileExtension Extension of file (.mp3)       
def getExtension(filename):
    (fileName, fileExtension) = os.path.splitext(filename)
    return fileExtension

# Replace the extension of a filename passed
#
# @param filename File name including extension
# @param extension Extension to replace with
# @return New filename with replaced extension    
def replaceExtension(filename, extension):
    (fileName, fileExtension) = os.path.splitext(filename)
    if extension[0] != '.':
        extension = '.%s' % extension
    return '%s%s' % (fileName, extension)

# Open a URL in the user's default browser
#
# @param url URL to open    
def openUrl(url):
    webbrowser.open(url)

# Determine what type of media a file name is
#
# @param filename File name to analyze
# @return 1, 2, 0 (Video, Audio, None)    
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

# Write a URL to history document
# 
# @param url URL to be written to history document        
def writeHistory(url):
    saveCurrent = open(HISTORY, 'r').readlines()
    writeNew = open(HISTORY, 'w')
    saveCurrent.append('%s\n' % url)
    writeNew.write(''.join(saveCurrent))
    writeNew.close()

# Send an email to <ritashugisha.diagnostics@gmail.com> for anonymous analytics
#
# @param procType Download process type
# @param downloadProc Download command used
# @param convertProc Convert command used
# @param downloadStdout Download PIPE text
def sendDiagnostics(procType, downloadProc, convertProc, downloadStdout):
    mailUser = 'ritashugisha.notification@gmail.com'
    mailPass = 'freenotification'
    mailTo = 'ritashugisha.diagnostics@gmail.com'
    mailSubject = 'LUXINATE @ %s' % getpass.getuser()
    mailMessage = [
    'Luxinate %s - %s <%s>\n' % (VERSION, AUTHOR, CONTACT),
    'User: %s\nPython: %s\nSystem: %s\n\n' % 
    (os.path.expanduser('~'), sys.version_info[0:3], sys.version.replace('\n', '_').replace(' ', '_')),
    '<<<GLOBAL>>>\nWorkflow: %s\nYouTube_DL: %s\nFFMPEG: %s\nNotifier: %s\nCocoaDialog: %s\n\n' %
    (CURRENT_PATH, os.path.exists(YOUTUBE_DL.replace('\ ', ' ')), os.path.exists(FFMPEG.replace('\ ', ' ')),
     os.path.exists(NOTIFIER.replace('\ ', ' ')), os.path.exists(COCOA.replace('\ ', ' '))),
    '<<<PARMS>>>\nDownload Path: %s\nDeafult Video: %s\nDefault Audio: %s\n\n' %
    (DOWNLOAD, FORMAT_VIDEO, FORMAT_AUDIO),
    '<<<HISTORY>>>\n%s\n\n' % (', '.join(open(HISTORY).readlines())),
    '<<<PROCTYPE>>>\n[%s]\nDownload Proc: %s\nConvert Proc: %s\n\n' % 
    (procType, downloadProc, convertProc),
    '<<<YOUTUBE_DL>>>\n%s\n\n' % downloadStdout,
    '<<<LISTDIR>>>\nos.path.exists(%s)\n%s\n' % (os.path.exists(DOWNLOAD), os.listdir(DOWNLOAD))
    ]
    mailFull = '\r\n'.join(['From: %s' % mailUser, 'To: %s' % mailTo, 'Subject: %s' % mailSubject, ''.join(mailMessage)])
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(mailUser, mailPass)
    server.sendmail(mailUser, mailTo, mailFull)
    server.quit()
                                                  