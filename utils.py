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

import os, sys, subprocess, base64
import urllib2, smtplib, urlparse
import getpass, webbrowser
import xml.etree.ElementTree as etree
progressBar = None

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

def spawnProgressBar():
    global progressBar
    progressBar = ProgressBar.ProgressBar('Luxinate', '100')
    progressBar.start()

# Run a download process from youtube-dl while displaying a progress bar
#
# @param downloadCmd Command for download
# @param mediaTitle Title of media
# @param quitFilter = True
def runProgressBarDownload(downloadCmd, quitFilter = True, spawnKill = True):
    global progressBar
    if spawnKill:
        spawnProgressBar()
    try:
        mediaTitle = open(TEMPFILE, 'r').readline()
        progressBar.update(mediaTitle)
        runDownload = subprocess.Popen([downloadCmd],
        stdout = subprocess.PIPE, shell = True)
        while runDownload.poll() is None:
            newLine = runDownload.stdout.readline()
            try:
                if newLine.split(' ')[2] == '':
                    newPercent = newLine.split(' ')[3].replace('%', '')
                else:
                    newPercent = newLine.split(' ')[2].replace('%', '')
                infoText = ' '.join(newLine.split(' ')[4:]).replace('\n', '')
            except IndexError:
                newPercent = '100'
                infoText = 'Download Complete'
            try:
                float(newPercent)
                progressBar.increment(mediaTitle, infoText, newPercent)
            except ValueError:
                pass
        progressBar.update('Download Complete')
        if quitFilter:
            progressBar.quit()
    except:
        pass
    if quitFilter:
        progressBar.quit()
        
# Run a convert progress while keeping the progress bar displayed
#
# @param convertCmd Command for convert
# @param mediaTitle Title of media        
def runProgressBarConvert(convertCmd, quitFilter = True):
    global progressBar
    try:
        mediaTitle = open(TEMPFILE, 'r').readline()
        progressBar.increment(mediaTitle, 'Converting...', '100')
        runProcess(convertCmd)
    except:
        progressBar.quit()
    if quitFilter:
        progressBar.quit()

# Kill the progress bar display    
def killProgressBar():
    global progressBar
    progressBar = ProgressBar.ProgressBar('Luxinate', '100')
    progressBar.quit()
    progressBar = None

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
    formatChars = ['!', '?', '$', '%', '#', '&', '*', ';', '(', ')', '@', '`', '|', "'", '"', '~', '<', '>']
    for i in formatChars:
        if i in string:
            string = string.replace(i, '\%s' % i)
    return string
def deformatConsole(string):
    formatChars = ['!', '?', '$', '%', '#', '&', '*', ';', '(', ')', '@', '`', '|', "'", '"', '~', '<', '>', ' ']
    for i in formatChars:
        if '\%s' % i in string:
            string = string.replace('\%s' % i, i)
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
VERSION           = '4.1.1'
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
PROGRESS_BAR      = '%s/Resources/Settings/progressBar' % CURRENT_PATH
ABOUT             = formatSpaces('%s/Resources/Settings/about' % CURRENT_PATH)
YOUTUBE_DL        = formatSpaces('%s/Resources/youtube-dl' % CURRENT_PATH)
FFMPEG            = formatSpaces('%s/Resources/ffmpeg' % CURRENT_PATH)
NOTIFIER          = formatSpaces('%s/Resources/Notifier.app/Contents/MacOS/terminal-notifier' % CURRENT_PATH)
COCOA             = formatSpaces('%s/Resources/CocoaDialog.app/Contents/MacOS/cocoadialog' % CURRENT_PATH)
SOUNDCLOUD_API    = 'c8332a9f3ad1ee47559ad6c09e63a9a8'
MAIL_USER         = 'cml0YXNodWdpc2hhLm5vdGlmaWNhdGlvbkBnbWFpbC5jb20='
MAIL_PASS         = 'ZnJlZW5vdGlmaWNhdGlvbg=='
MAIL_TO           = 'cml0YXNodWdpc2hhLmRpYWdub3N0aWNzQGdtYWlsLmNvbQ=='
sys.path.insert(0, '%s/Resources/ProgressBar.scptd/Contents/Resources/' % CURRENT_PATH)
import ProgressBar
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
    if not os.path.exists(PROGRESS_BAR):
        os.system('touch %s' % PROGRESS_BAR)
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
    if len(open(PROGRESS_BAR, 'r').readline()) == 0:
        PROGRESS = False
    else:
        PROGRESS = True
except IOError:
    DOWNLOAD = formatSpaces('%s%s' % (os.path.expanduser('~'), '/Downloads/'))
    FORMAT_VIDEO = ''
    FORMAT_AUDIO = ''
    PROGRESS = False
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

# Validate and return formatted dictionary from string
#
# @param string String dictionary
def validateStringDict(string):
    try:
        return ast.literal_eval(string)
    except:
        return False

# Return domain of URL
#
# @param url URL to check
def checkDomain(url):
    if 'www' in urlparse.urlparse(url).netloc[0:3].lower():
        urlDomain = urlparse.urlparse(url).netloc.split('.', 2)[1].lower()
    else:
        urlDomain = urlparse.urlparse(url).netloc.split('.', 2)[0].lower()
    if 'soundcloud' in urlDomain:
        return 'soundcloud'
    elif 'youtube' in urlDomain:
        return 'youtube'
    else:
        return False

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

# Format URL for command line use
#
# @param url URL to be formatted
# @return url Formatted URL
def formatUrl(url):
    parsedUrl = urlparse.urlparse(url)
    if 'youtube' in parsedUrl.netloc.split('.', 2)[1].lower():
        if '&' in parsedUrl.query:
            return '%s://%s%s?%s%s' % (parsedUrl.scheme, parsedUrl.netloc, parsedUrl.path, parsedUrl.params, parsedUrl.query.split('&')[0])
        else:
            return url
    else:
        return url

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
    if "'" in url[0]:
        url = url[1:-1]
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

# Write a URL to the temporary file
#
# @param url URL to be written to temporary file
def writeTemp(url):
    writeBump = open(TEMPFILE, 'w')
    writeBump.write(url)
    writeBump.close()

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
    mailSubject = 'Luxinate%s @ %s' % (VERSION, getpass.getuser())
    mailMessage = [
    '<generic>\n\tUser:\t%s\n\tPython:\t%s\n\tSystem:\t%s\n\n' % (os.path.expanduser('~'), sys.version_info[0:3], sys.version.split('\n')[1]),
    '<third-party>\n\tyoutube-dl:\t%s\n\tffmpeg:\t\t%s\n\tnotifier:\t\t%s\n\tcocoadialog:\t%s\n\n' % (os.path.exists(YOUTUBE_DL.replace('\ ', ' ')),
     os.path.exists(FFMPEG.replace('\ ', ' ')), os.path.exists(NOTIFIER.replace('\ ', ' ')), os.path.exists(COCOA.replace('\ ', ' '))),
    '<settings>\n\tDownloadPath:\t%s\n\tVideoDefault:\t%s\n\tAudioDefault:\t%s\n\n' % (DOWNLOAD, FORMAT_VIDEO, FORMAT_AUDIO),
    '%s\n' % ''.join(open(HISTORY).readlines()),
    '<download>\n\tProcType:\t\t%s\n\tDownloadProc:\t%s\n\tConvertProc:\t\t%s\n\n' % (procType, downloadProc, convertProc),
    '%s' % '\n'.join(os.listdir(DOWNLOAD))
    ]
    mailFull = '\r\n'.join(['From: %s' % base64.b64decode(MAIL_USER), 'To: %s' % base64.b64decode(MAIL_TO), 
    'Subject: %s' % mailSubject, ''.join(mailMessage)])
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(base64.b64decode(MAIL_USER), base64.b64decode(MAIL_PASS))
    server.sendmail(base64.b64decode(MAIL_USER), base64.b64decode(MAIL_TO), mailFull)
    server.quit()
