#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# @author  Ritashugisha
# @contact ritashugisha@gmail.com
# @program Luxinate - Alfred.v2 YouTube Downloader
# @version <TBA>
#
# Luxinate - Alfred.v2 YouTube Downloader
# Copyright (C) 2014 Ritashugisha
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import pickle
import tempfile
import subprocess
import inspect
import logging
import urlparse
import urllib2
import xml.etree.ElementTree as etree
import xml.dom.minidom as dom
from datetime import datetime as curtime
from time import strftime as ftime
from time import time as unixtime

# [Global Variables]
AUTHOR      = 'Ritashugisha'
CONTACT     = 'ritashugisha@gmail.com'
PROGRAM     = 'Luxinate'
DESCRIPTION = 'Alfred.v2 YouTube Downloader'
VERSION     = '7.0'
RELEASE     = '1.0a'
DISCLAIMER  = '%s Ritashugisha - Luxinate' % curtime.now().strftime('%Y')
ABOUT       = '''ABOUT HERE'''

# [Program Variables]
TMP 	= '/tmp/Luxinate/'
TMP_LOG = '%slogs/' % TMP
TMP_OBJ = '%sobjs/' % TMP
LOG 	= '%slux_%s.log' % (TMP_LOG, ftime('%Y-%m-%d'))
PICKLE  = '%sluxTransferObject.pickle' % TMP_OBJ

# [Logging Setup]
if __name__ in '__main__':
    for i in [TMP, TMP_LOG, TMP_OBJ, LOG, PICKLE]:
        if not os.path.exists(i):
            if i[-1] != '/':
                os.system('touch %s' % i)
            else:
                os.system('mkdir %s' % i)
    logging.basicConfig(level = logging.DEBUG,
        format = '[%(asctime)s] %(levelname)-8s ....%(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        filename = LOG)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter('[%(levelname)-8s] ....%(message)s'))
    logging.getLogger('').addHandler(console)
    reload(sys)
    sys.setdefaultencoding('utf-8')

"""
.. py:function Logger()
Generate a logging object during runtime.
"""
def Logger(function):
    return logging.getLogger(function)


"""
.. py:class Feedback()
Used to build an XML formatted feedback for Alfred's script filter function.
"""
class Feedback():

    """
    .. py:fucntion __init__(self)
    Feedback element for script filter feedback.
    """
    def __init__(self):
        self.log = Logger('feedback')
        self.feedback = etree.Element('items')
        self.log.info('built feedback object at (%s)' % self.feedback)

    """
    .. py:function __repr__(self)
    Return the parsed script filter feedback as string.
    """
    def __repr__(self):
        self.log.info('retrieving feedback object at (%s)...' % self.feedback)
        result = etree.tostring(self.feedback)
        self.log.info('....%s' % result)
        return result

    """
    .. py:function addItem(self, title, subtitle='', arg='', valid='yes', autocompltet='', icon='icon.png')
    Add an item for script filter feedback.

    :param str title: Title of item
    :param str subtitle: Subtitle of item
    :param str arg: Passed argument of item
    :param str valid: "yes" if valid item, "no" if invalid item
    :param str autocomplete: "yes" if item autocompletes
    :param str icon: Icon file location of item
    """
    def addItem(self, title, subtitle = '', arg = '', valid = 'yes', autocomplete = '', icon = 'icon.png'):
        self.log.info('addding item to feedback object at (%s)...' % self.feedback)
        self.log.info('....{"title":"%s", "subtitle":"%s", "arg":"%s", "icon":"%s"}' % (title, subtitle, arg, icon))
        item = etree.SubElement(self.feedback, 'item', uid = str(len(self.feedback)), arg = arg, valid = valid, autocomplete = autocomplete)
        itemTitle = etree.SubElement(item, 'title')
        itemTitle.text = title
        itemSubtitle = etree.SubElement(item, 'subtitle')
        itemSubtitle.text = subtitle
        itemIcon = etree.SubElement(item, 'icon')
        itemIcon.text = icon


"""
.. py:class Config()
Manage and edit Luxinate's configuration.
"""
class Config():

    """
    .. py:function __init__(self, config)
    Open or write a new configuration file for Luxinate.

    :param str config: File location of configuration file
    """
    def __init__(self, config):
        self.log = Logger('config')
        self.utils = Utils()
        self.config = config
        if not os.path.exists(self.config) or len(open(self.config, 'r').read()) <= 0:
            self.log.info('config does not exist at (%s)' % self.config)
            os.system('touch %s' % self.utils.formatConsole(self.config))
            self.buildTemplate()

    """
    .. py:function write(self, xmlRoot)
    Write the ElementTree root to configuration file.

    :param ElementTree xmlRoot: Root of configuration XML
    """
    def write(self, xmlRoot):
        bump = open(self.config, 'w+')
        bump.write(dom.parseString(etree.tostring(xmlRoot, 'utf-8')).toxml())
        bump.close()

    """
    .. py:function getRoot(self)
    Return the ElementTree root of the configuration file.
    """
    def getRoot(self):
        return etree.ElementTree(file = self.config).getroot()

    """
    .. py:function buildTemplate(self)
    Build the basetemplate of Luxinate's XML configuration file.
    """
    def buildTemplate(self):
        self.log.info('building config at (%s)' % self.config)
        root = etree.Element('root')
        info = etree.SubElement(root, 'info')
        author = etree.SubElement(info, 'author')
        author.set('contact', CONTACT)
        author.text = AUTHOR
        version = etree.SubElement(info, 'version')
        version.set('release', RELEASE)
        version.text = VERSION
        program = etree.SubElement(info, 'program')
        program.set('description', DESCRIPTION)
        program.text = PROGRAM
        settings = etree.SubElement(root, 'settings')
        download_dir = etree.SubElement(settings, 'download_dir')
        download_dir.set('default', '%s/Downloads/' % os.path.expanduser('~'))
        download_dir.text = download_dir.attrib['default']
        video_opt = etree.SubElement(settings, 'video_opt')
        video_opt.set('default', '-1')
        video_opt.text = video_opt.attrib['default']
        audio_opt = etree.SubElement(settings, 'audio_opt')
        audio_opt.set('default', '.mp3')
        audio_opt.text = audio_opt.attrib['default']
        progress_bar = etree.SubElement(settings, 'progress_bar')
        progress_bar.set('default', 'False')
        progress_bar.text = progress_bar.attrib['default']
        history = etree.SubElement(root, 'history')
        history.set('results', '0')
        about = etree.SubElement(root, 'about')
        about.text = ABOUT
        self.write(root)
        self.log.info('config built at (%s)' % self.config)

    """
    .. py:function getAbout(self)
    Retreive the about from the configuration file.
    """
    def getAbout(self):
        self.log.info('retrieving %s about' % PROGRAM)
        root = self.getRoot()
        return root.find('.//about').text

    """
    .. py:function addHistoryEntry(self, title, url)
    Add a new history entry to the configuration file.

    :param str title: Title of media
    :param str url: URL of media
    """
    def addHistoryEntry(self, title, url):
        self.log.info('adding history entry {"title":"%s", "url":"%s"}' % (title, url))
        root = self.getRoot()
        history = root.find('.//history')
        entry = etree.SubElement(history, 'entry')
        entry.set('title', title.decode('utf-8'))
        entry.set('time', str(unixtime()))
        entry.text = url
        history.set('results', str(int(history.attrib['results']) + 1))
        self.write(root)

    """
    .. py:function getHistory(self)
    Return the history entries as a list of dictionaries.
    """
    def getHistory(self):
        history = self.getRoot().find('.//history')
        self.log.info('retrieving [%s] results from history' % history.attrib['results'])
        result = []
        for i in history.findall('entry'):
            entry = {}
            entry['title'] = i.attrib['title']
            entry['time'] = i.attrib['time']
            entry['url'] = i.text
            result.append(entry)
        return result

    """
    .. py:function clearHistory(self)
    Clear all history entries from the configuration file.
    """
    def clearHistory(self):
        root = self.getRoot()
        history = root.find('.//history')
        self.log.info('deleting [%s] results from history...' % history.attrib['results'])
        for i in history.findall('entry'):
            self.log.info('....removing {"title":"%s", "url":"%s"} from history' % (i.attrib['title'], i.text))
            history.remove(i)
        history.set('results', '0')
        self.write(root)

    """
    .. py:function toggleProgressBar(self)
    Toggle the progress bar setting from true to false.
    """
    def toggleProgressBar(self):
        root = self.getRoot()
        progress_bar = root.find('.//progress_bar')
        if 'f' in progress_bar.text[0].lower():
            progress_bar.text = 'True'
        else:
            progress_bar.text = 'False'
        self.log.info('toggled progress_bar to (%s)' % progress_bar.text)
        self.write(root)

    """
    .. py:function getProgressBar(self)
    Return the current boolean value of the progress bar.
    """
    def getProgressBar(self):
        self.log.info('retrieving value of progress_bar')
        return 't' in self.getRoot().find('.//progress_bar').text[0].lower()

    """
    .. py:function editDownloadDir(self, directory, default=False)
    Change the value of the download directory in the configuration.

    :param str directory: New directory location
    :param bool default: True if revert to default value, False otherwise
    """
    def editDownloadDir(self, directory, default = False):
        root = self.getRoot()
        download_dir = root.find('.//download_dir')
        if not default:
            if directory[:-1] != '/':
                directory = '%s/' % directory
            download_dir.text = directory
        else:
            download_dir.text = download_dir.attrib['default']
        self.log.info('changed download_dir to (%s)' % download_dir.text)
        self.write(root)

    """
    .. py:function getDownloadDir(self)
    Return the current download location.
    """
    def getDownloadDir(self):
        self.log.info('retrieving value of download_dir')
        return self.getRoot().find('.//download_dir').text

    """
    .. py:function editVideoOpt(self, opt, default=False)
    Change the value of the video option in the configuration.

    :param str opt: New option for video
    :param bool default: True if revert to default value, False otherwise
    """
    def editVideoOpt(self, opt, default = False):
        root = self.getRoot()
        video_opt = root.find('.//video_opt')
        if not default:
            video_opt.text = opt
        else:
            video_opt.text = video_opt.attrib['default']
        self.log.info('changed video_opt to (%s)' % video_opt.text)
        self.write(root)

    """
    .. py:function getVideoOpt(self)
    Get the current video option.
    """
    def getVideoOpt(self):
        self.log.info('retireving value of video_opt')
        return self.getRoot().find('.//video_opt').text

    """
    .. py:function editAudioOpt(self, opt, default=False)
    Change the value of the audio option in the configuration.

    :param str opt: New option for audio
    :param bool default: True if revert to default value, False otherwise
    """
    def editAudioOpt(self, opt, default = False):
        root = self.getRoot()
        audio_opt = root.find('.//audio_opt')
        if not default:
            audio_opt.text = opt
        else:
            audio_opt.text = audio_opt.attrib['default']
        self.log.info('changed audio_opt to (%s)' % audio_opt.text)
        self.write(root)

    """
    .. py:function getAudioOpt(self)
    Get the current audio option.
    """
    def getAudioOpt(self):
        self.log.info('retrieving value of audio_opt')
        return self.getRoot().find('.//audio_opt').text


"""
.. py:class Utils()
Used for preforming system operations.
"""
class Utils():

    """
    .. py:function __init__(self)
    Initialize the Utils object.
    """
    def __init__(self):
	   self.log = Logger('utils')

    """
    .. py:function runProcess(self, process)
    Run a subprocess on the system.

    :param str process: Process to be run
    """
    def runProcess(self, process):
        self.log.info('running subprocess (%s)' % process)
        proc = subprocess.Popen([process], stdout = subprocess.PIPE, shell = True)
        (proc, proc_e) = proc.communicate()
        return proc

    """
    .. py:function runOsascript(self, script)
    Run an osascript on the system via subprocess.

    :param str script: Osascript to be run
    """
    def runOsascript(self, script):
        self.log.info('running osascript (%s)' % script)
        proc = self.runProcess('osascript -e \'%s\'' % script)
        return proc

    """
    .. py:function formatConsole(self, string)
    Escape unfriendly characters from a string.

    :param str string: String to be escaped
    """
    def formatConsole(self, string):
        bannedChars = ['!', '?', '$', '%', '#', '&', '*', ';', '(', ')', '@', '`', '|', "'", '"', '~', '<', '>', ' ']
        for i in bannedChars:
            if i in string:
                string = string.replace(i, '\%s' % i)
        return string

    """
    .. py:function replaceExtension(self, filename, extension)
    Replace and return a filename's extension.

    :param str filename: Filename to change
    :param str extension: New extension of filename
    """
    def replaceExtension(self, filename, extension):
        if extension[0] != '.':
            extension = '.%s' % extension
        return '%s%s' % (os.path.splitext(filename)[0], extension)


"""
.. py:class PickleTransfer()
Used to transfer object data from Luxinate to Download in pickle form.
"""
class PickleTransfer():

    """
    .. py:function __init__(self, mediatitle, mediafile, mediaurl)
    Build an object used for pickle transfer.

    :param str mediatitle: Title of the media
    :param str mediafile: Filename of the media
    :param str mediaurl: URL of the media
    """
    def __init__(self, mediatitle, mediafile, mediaurl):
        self.mediatitle = mediatitle
        self.mediafile = mediafile
        self.mediaurl = mediaurl


"""
.. py:class binaries()
Used for pretty much everything.
"""
class Binaries():

    """
    .. py:function __init__(self)
    Initialize a new set of binaries for any calling class.
    """
    def __init__(self):
        self.log          = Logger('binaries')
        self.log.info('initialized new set of binaries')
        self.workflow     = '%s/' % os.path.dirname(os.path.abspath(__file__))
        self.config       = Config('%s_config.xml' % self.workflow)
        self.resources    = '%sResources/' % self.workflow
        self.icons        = '%sIcons/' % self.resources
        self.pkgmanager   = '%sLuxePrisimPackageManager' % self.workflow
        self.glyphmanager = '%sGlyphManager' % self.workflow
        self.id3tag       = '%sid3tag' % self.resources
        self.youtube_dl   = '%syoutube-dl' % self.resources
        self.ffmpeg       = '%sffmpeg' % self.resources
        self.sender       = 'com.runningwithcrayons.Alfred-2'
        self.cocoa        = Cocoa('/Applications/cocoaDialog.app/Contents/MacOS/cocoadialog')
        self.notifier     = Notifier('/Applications/terminal-notifier.app/Contents/MacOS/terminal-notifier')
        self.dependencies = [
            {'title':'mstratman.cocoadialog', 'dest':'/Applications', 'loci':self.cocoa.cocoa},
            {'title':'alloy.terminal-notifier', 'dest':'/Applications', 'loci':self.notifier.notifier},
            {'title':'ritashugisha.glyphmanager', 'dest':self.workflow, 'loci':self.glyphmanager},
            {'title':'rg3.youtube-dl', 'dest':self.resources, 'loci':self.youtube_dl},
            {'title':'tessus.ffmpeg', 'dest':self.resources, 'loci':self.ffmpeg},
            {'title':'ritashugisha.luxinateicons', 'dest':self.resources, 'loci':self.icons},
            {'title':'ritashugisha.id3tag', 'dest':self.resources, 'loci':self.id3tag}]
        self.typeVideo    = ['.flv', '.mp4', '.mov', '.avi', '.mpeg', '.wmv']
        self.typeAudio    = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.wma', '.mp2', '.acc', '.aiff']


"""
.. py:class Luxinate()
Used to perform interaction with Alfred.
"""
class Luxinate():

    """
    .. py:function __init__(self)
    Initialized the Luxinate object.
    """
    def __init__(self):
        self.log      = Logger('luxinate')
        self.utils    = Utils()
        self.binaries = Binaries()
        self.startUp()

    def buildTransfer(self, mediatitle, mediafile, mediaurl):
        pickle.dump(PickleTransfer(mediatitle, mediafile, mediaurl), open(PICKLE, 'w'))

    def hasConnection(self):
        try:
            urllib2.urlopen('http://74.125.228.100', timeout = 1)
            return True
        except urllib2.URLError:
            pass
        return False

    def validUrl(self, url):
        if 'http' in urlparse.urlparse(url).scheme:
            try:
                urllib2.urlopen(url, timeout = 2)
                return True
            except urllib2.URLError:
                pass
        return False

    def supportedUrl(self, url):
        try:
            url = urlparse.urlparse(url)
            test1 = url.hostname.split('.')[1]
            test2 = '%s%s' % (test1, url.path.replace('/', ':'))
            for i in self.utils.runProcess('%s --list-extractors' % self.utils.formatConsole(self.binaries.youtube_dl)).split('\n')[:-1]:
                if test1.lower() in i.lower() or test2.lower() in i.lower():
                    return True
            return False
        except AttributeError:
            return False

    def getMediaInfo(self, url):
        try:
            return self.utils.runProcess('%s --get-title --get-filename %s' % (self.utils.formatConsole(self.binaries.youtube_dl), url)).split('\n')[:-1]
        except:
            return False

    def getMediaType(self, mediafile):
        (fileName, fileExtension) = os.path.splitext(mediafile)
        if fileExtension.lower() in self.binaries.typeVideo:
            return 1
        elif fileExtension.lower() in self.binaries.typeAudio:
            return 2
        else:
            return 0

    def default(self, url):
        if self.hasConnection and self.validUrl(url) and self.supportedUrl(url):
            feed = Feedback()
            try:
                (mediatitle, mediafile) = self.getMediaInfo(url)
                self.buildTransfer(mediatitle, mediafile, url)
                mediaType = self.getMediaType(mediafile)
                if mediaType == 1:
                    feed.addItem('Download Video', mediatitle, '', '', '', '%s_video.png' % self.binaries.icons)
                    feed.addItem('Download Audio', mediatitle, '', '', '', '%s_audio.png' % self.binaries.icons)
                    feed.addItem('Download Video and Audio', mediatitle, '', '', '', '%s_both.png' % self.binaries.icons)
                elif mediaType == 2:
                    feed.addItem('Download Audio', mediatitle, '', '', '', '%s_audio.png' % self.binaries.icons)
                else:
                    feed.addItem('Unknown Media Type', 'Please report to %s' % AUTHOR, '', '', '', '%s_x.png' % self.binaries.icons)
            except ValueError:
                 feed.addItem('Invalid URL', 'No available downloads from %s' % url, '', '', '', '%s_x.png' % self.binaries.icons)
        return feed


    """
    .. py:function startUp(self)
    Used to check that the program's environment is in order before running.
    """
    def startUp(self):
        if not os.path.exists(self.binaries.resources):
            os.system('mkdir %s' % self.utils.formatConsole(self.binaries.resources))
        if not os.path.exists(self.binaries.pkgmanager):
            self.log.critical('cannot find package manager at (%s)' % self.binaries.pkgmanager)
            if not os.path.exists(self.binaries.cocoa.cocoa):
                if not os.path.exists(self.binaries.notifier.notifier):
                    self.utils.runOsascript('tell application "Alfred 2" to search "Error: missing package manager"')
                else:
					self.binaries.notifier.notification(title = 'Luxinate', subtitle = u'\u26A0 WARNING \u26A0',
						message = 'Missing package manager...', sender = self.sender, group = 'lux.warning')
            else:
				self.binaries.cocoa.msgbox(title = 'Luxinate', text = u'\u26A0 WARNING \u26A0',
					informative_text = 'Missing package manager...', button1 = 'Ok')
            sys.exit(0)
        missingDependencies = []
        for i in self.binaries.dependencies:
            if not os.path.exists(i['loci']):
                self.log.critical('cannot find dependency "%s" at (%s)' % (i['title'], i['loci']))
                missingDependencies.append(i)
        if len(missingDependencies) > 0:
            for i in missingDependencies:
                self.utils.runProcess('%s -i %s -o %s' % (self.utils.formatConsole(self.binaries.pkgmanager), 
                    i['title'], self.utils.formatConsole(i['dest'])))


"""
.. py:class Download()
Used to automate downloads.
"""
class Download():

    """
    .. py:function __init__(self)
    Initialize the Download object.
    """
    def __init__(self):
        self.log      = Logger('download')
        self.utils    = Utils()
        self.binaries = Binaries()
        self.download = pickle.load(open(PICKLE, 'r'))

    """
    .. py:function postTag(self)
    Tag any audio files with warning information.
    """
    def postTag(self, filepath):
        if os.path.splitext(self.download.mediafile)[1].lower() in self.binaries.typeAudio:
            self.log.info('adding program copyright protection tag')
            self.utils.runProcess('%s -s "%s" -c "%s" -C "%s" -y "%s" %s' % (self.utils.formatConsole(self.binaries.id3tag),
                self.download.mediatitle, DISCLAIMER, DISCLAIMER, curtime.now().strftime('%Y'), self.utils.formatConsole(filepath)))

    """
    .. py:function defaultVideo(self)
    Downloads the video read from self.download PICKLE object
    """
    def defaultVideo(self):
        self.binaries.config.addHistoryEntry(self.download.mediatitle, self.download.mediaurl)
        if int(self.binaries.config.getVideoOpt()) != -1:
            self.log.info('setting up download with video opt (%s)' % self.binaries.config.getVideoOpt())
            downloadProc = 'cd %s;%s -itf %s %s' % (self.utils.formatConsole(self.binaries.config.getDownloadDir()), self.utils.formatConsole(self.binaries.youtube_dl), 
                self.binaries.config.getVideoOpt(), self.download.mediaurl)
        else:
            self.log.info('setting up default download')
            downloadProc = 'cd %s;%s -it %s' % (self.utils.formatConsole(self.binaries.config.getDownloadDir()), self.utils.formatConsole(self.binaries.youtube_dl), 
                self.download.mediaurl)
        if self.binaries.config.getProgressBar():
            self.log.info('download to be run with progressbar')
            downloadProc = '%s --newline' % downloadProc
            # TODO: Implement progress bar
        else:
            self.binaries.notifier.notification(title = PROGRAM, subtitle = '► Downloading Video', sender = self.binaries.sender,
                message = self.download.mediatitle, sound = '')
            self.utils.runProcess(downloadProc)
        self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Download Complete', sender = self.binaries.sender,
            message = self.download.mediatitle, sound = 'Glass')

    """
    .. py:function defaultAudio(self)
    Downloads (and converts) the audio read from self.download PICKLE object
    """
    def defaultAudio(self):
        self.binaries.config.addHistoryEntry(self.download.mediatitle, self.download.mediaurl)
        passConvert = False
        if os.path.splitext(self.download.mediafile)[1].lower() in self.binaries.typeAudio and os.path.splitext(
            self.download.mediafile)[1].lower() in self.binaries.config.getAudioOpt():
            self.log.info('setting up download with no conversion for (%s)' % self.download.mediafile)
            passConvert = True
        tempLux = tempfile.mkstemp(dir = TMP, prefix = 'tmp_')[1]
        self.utils.runProcess('rm -rf %s' % tempLux)
        if not passConvert:
            downloadProc = '%s -i %s -o %s' % (self.utils.formatConsole(self.binaries.youtube_dl), self.download.mediaurl, tempLux)
            if '.mp3' in self.binaries.config.getAudioOpt():
                self.log.info('setting up conversion of (.mp3) for (%s)' % self.download.mediafile)
                convertProc = '%s -y -i %s -b:a 320k %s' % (self.utils.formatConsole(self.binaries.ffmpeg), tempLux, 
                    self.utils.formatConsole(self.utils.replaceExtension('%s%s' % (self.binaries.config.getDownloadDir(), 
                        self.download.mediafile), self.binaries.config.getAudioOpt())))
            else:
                self.log.info('setting up conversion of (%s) for (%s)' % (self.binaries.config.getAudioOpt(), self.download.mediafile))
                convertProc = '%s -y -i %s %s' % (self.utils.formatConsole(self.binaries.ffmpeg), tempLux, 
                    self.utils.formatConsole(self.utils.replaceExtension('%s%s' % (self.binaries.config.getDownloadDir(), 
                        self.download.mediafile), self.binaries.config.getAudioOpt())))
        else:
            downloadProc = 'cd %s;%s -it %s' % (self.utils.formatConsole(self.binaries.config.getDownloadDir()), 
                self.utils.formatConsole(self.binaries.youtube_dl), self.download.mediaurl)
            convertProc = ''
        if self.binaries.config.getProgressBar():
            self.log.info('download to be run with progressbar')
            downloadProc = '%s --newline' % downloadProc
            if not passConvert:
                self.log.info('convert to be run with progressbar')
                pass
                # TODO: Implement "non-stop" progress bar
            else:
                pass
                # TODO: Implement progress bar
        else:
            self.binaries.notifier.notification(title = PROGRAM, subtitle = '► Downloading Audio', sender = self.binaries.sender,
                message = self.download.mediatitle, sound = '')
            self.utils.runProcess(downloadProc)
            if not passConvert:
                self.utils.runProcess(convertProc)
        self.utils.runProcess('rm -rf %s' % tempLux)
        self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Download Complete', sender = self.binaries.sender, 
            message = self.download.mediatitle, sound = 'Glass')
        self.postTag(self.utils.replaceExtension('%s%s' % (self.binaries.config.getDownloadDir(), self.download.mediafile), self.binaries.config.getAudioOpt()))

    """
    .. py:function defaultVideo_Audio(self)
    Downloads the video and converts to audio from read from self.download PICKLE object
    """
    def defaultVideo_Audio(self):
        self.binaries.config.addHistoryEntry(self.download.mediatitle, self.download.mediaurl)
        if int(self.binaries.config.getVideoOpt()) != -1:
            self.log.info('setting up download with video opt (%s)' % self.binaries.config.getVideoOpt())
            downloadProc = 'cd %s;%s -itf %s %s' % (self.utils.formatConsole(self.binaries.config.getDownloadDir()), 
                self.utils.formatConsole(self.binaries.youtube_dl), self.binaries.config.getVideoOpt(), self.download.mediaurl)
        else:
            self.log.info('setting up default download')
            downloadProc = 'cd %s;%s -it %s' % (self.utils.formatConsole(self.binaries.config.getDownloadDir()), self.utils.formatConsole(self.binaries.youtube_dl), 
                self.download.mediaurl)
        if '.mp3' in self.binaries.config.getAudioOpt():
            convertProc = '%s -y -i %s -b:a 320k %s' % (self.utils.formatConsole(self.binaries.ffmpeg), 
                self.utils.formatConsole('%s%s' % (self.binaries.config.getDownloadDir(), self.download.mediafile)),
                self.utils.formatConsole(self.utils.replaceExtension('%s%s' % (self.binaries.config.getDownloadDir(), 
                    self.download.mediafile), self.binaries.config.getAudioOpt())))
        else:
            convertProc = '%s -y -i %s %s' % (self.utils.formatConsole(self.binaries.ffmpeg), 
                self.utils.formatConsole('%s%s' % (self.binaries.config.getDownloadDir(), self.download.mediafile)),
                self.utils.formatConsole(self.utils.replaceExtension('%s%s' % (self.binaries.config.getDownloadDir(),
                    self.download.mediafile), self.binaries.config.getAudioOpt())))
        if self.binaries.config.getProgressBar():
            downloadProc = '%s --newline' % downloadProc
            # TODO: Implement "non-stop" progress bar
            # Convert command (progress bar) here too
        else:
            self.binaries.notifier.notification(title = PROGRAM, subtitle = '► Downloading Video', sender = self.binaries.sender,
                message = self.download.mediatitle, sound = '')
            self.utils.runProcess(downloadProc)
            self.binaries.notifier.notification(title = PROGRAM, subtitle = '► Downloading Audio', sender = self.binaries.sender, 
                message = self.download.mediatitle, sound = '')
            self.utils.runProcess(convertProc)
        self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Download Complete', sender = self.binaries.sender, 
            message = self.download.mediatitle, sound = 'Glass')
        self.postTag(self.utils.replaceExtension('%s%s' % (self.binaries.config.getDownloadDir(), self.download.mediafile), self.binaries.config.getAudioOpt()))


"""
.. py:class Cocoa()
Used to display cocoa dialogs from Luxinate.
"""
class Cocoa():

    """
    .. py:function __init__(self, cocoa)
    Initialize the Cocoa object.

    :param str cocoa: Path to cocoadialog binary
    """
    def __init__(self, cocoa):
		self.log = Logger('cocoa')
		self.utils = Utils()
		self.cocoa = cocoa

    def displayCocoa(self, funct, args, values):
        process = '%s %s' % (self.cocoa, funct.replace('_', '-'))
        for i in args[1:]:
            if (isinstance(values[i], str) or isinstance(values[i], list)) and len(values[i]) > 0:
                if isinstance(values[i], list):
                    values[i] = '" "'.join(values[i])
                process = '%s --%s "%s"' % (process, i.replace('_', '-'), values[i])
            elif isinstance(values[i], bool) and values[i]:
                process = '%s --%s' % (process, i.replace('_', '-'))
            else:
                pass
        self.log.info('displaying %s' % funct)
        try:
            return self.utils.runProcess(process).split('\n')[:-1]
        except IndexError:
            return False

    def checkbox(self, button1 = '', button2 = '', button3 = '', cancel = False, checked = [], columns = '', debug = False, disabled = [], height = '', icon = '', 
        icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', items = [], label = '', minimize = False, mixed = False, no_float = False,
        no_newline = False, posX = '', posY = '', quiet = False, resize = False, rows = '', string_output = False, timeout = '', timeout_format = '', title = '',
        value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(items) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (items)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)
    
    def msgbox(self, text = '', button1 = '', button2 = '', button3 = '', cancel = False, debub = False, empty_text = '', height = '', icon = '',
        icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_float = False, no_newline = False,
        posX = '', posY = '', quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '', value_required = '', width = '',
        informative_text = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(text) <= 0 or len(informative_text) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (text) and (informative_text)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def dropdown(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', exit_onchange = False, height = '', icon = '',
        icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', items = [], label = '', minimize = False, no_float = False, no_newline = False,
        posX = '', posY = '', pulldown = False, quiet = False, resize = False, selected = '', string_output = False, timeout = '', timeout_format = '', title = '',
        value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(items) <= 0 or len(label) <=0 :
            self.log.warning('must provide values for (button1) and (title) and (items) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def filesave(self, debug = False, height = '', icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', 
        minimize = False, no_create_directories = False, no_float = False, no_newline = False, packages_as_directories = False, posX = '', posY = '', 
        quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '', width = '', with_directory = '', 
        with_extensions = [], with_file = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def fileselect(self, debug = False, height = '', icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '',
        minimize = False, no_float = False, no_newline = False, no_select_directories = False, no_select_multiple = False, packages_as_directories = False, 
        posX = '', posY = '', quiet = False, resize = False, select_directories = False, select_multiple = False, select_only_directories = False, 
        string_output = False, timeout = '', timeout_format = '', title = '', width = '', with_directory = '', with_extensions = [], with_file = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def inputbox(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', height = '', icon = '', icon_file = '', 
        icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_float = False, no_newline = False, no_show = False,
        not_selected = False, posX = '', posY = '', quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '',
        value = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def ok_msgbox(self, alert = '', button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', height = '', icon = '',
        icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_cancel = False, no_float = False,
        no_newline = False, posX = '', posY = '', quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '', 
        value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def progressbar(self, debug = False, float = False, height = '', icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '',
        indeterminate = False, minimize = False, no_float = False, no_newline = False, percent = '', posX = '', posY = '', quiet = False, resize = False, stoppable = False,
        string_output = False, text = '', timeout = '', timeout_format = '', title = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def radio(self, allow_mixed = False, button1 = '', button2 = '', button3 = '', cancel = False, columns = '', debug = False, disabled = [], empty_text = '',
        height = '', icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', items = [], label = '', minimize = False, 
        mixed = False, no_float = False, no_newline = False, posX = '', posY = '', quiet = False, resize = False, rows = '', selected = '', string_output = False,
        timeout = '', timeout_format = '', title = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def secure_inputbox(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', height = '', icon = '', icon_file = '', 
        icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_float = False, no_newline = False, no_show = False,
        not_selected = False, posX = '', posY = '', quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '', value = '',
        value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def secure_standard_inputbox(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', height = '', icon = '', icon_file = '', 
        icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_float = False, no_newline = False, no_show = False,
        posX = '', posY = '', quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '', value = '', selected = '', 
        value_required = '', width = '', no_cancel = False):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def slider(self, always_show_value = False, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', empty_value = '', 
        height = '', icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', max = '', min = '', minimize = False,
        no_float = False, no_newline = False, posX = '', posY = '', quiet = False, resize = False, return_float = False, slider_label = '', string_output = False,
        ticks = '', timeout = '', timeout_format = '', title = '', value = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def standard_dropdown(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', exit_onchange = False, height = '',
        icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', items = [], label = '', minimize = False, no_cancel = False,
        no_float = False, no_newline = False, posX = '', posY = '', pulldown = False, quiet = False, resize = False, selected = '', string_output = False, 
        timeout = '', timeout_format = '', title = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def standard_inputbox(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', height = '', icon = '', icon_file = '',
        icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_cancel = False, no_float = False, no_newline = False,
        no_show = False, posX = '', posY = '', quiet = False, resize = False, selected = '', string_output = False, timeout = '', timeout_format = '', title = '',
        value = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def textbox(self, button1 = '', button2 = '', button3 = '', cancel = False, debug = False, editable = False, empty_text = '', focus_textbox = False, height = '',
        icon = '', icon_file = '', icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_editable = False, no_float = False,
        no_newline = False, posX = '', posY = '', quiet = False, resize = False, scroll_to = '', selected = '', string_output = False, text = '', text_from_file = '',
        timeout = '', timeout_format = '', title = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)

    def yesno_msgbox(self, alert = '', button1 = '', button2 = '', button3 = '', cancel = False, debug = False, empty_text = '', height = '', icon = '', icon_file = '',
        icon_height = '', icon_size = '', icon_type = '', icon_width = '', label = '', minimize = False, no_cancel = False, no_float = False, no_newline = False,
        posX = '', posY = '', quiet = False, resize = False, string_output = False, timeout = '', timeout_format = '', title = '', value_required = '', width = ''):
        frame = inspect.currentframe()
        funct = inspect.getframeinfo(frame)[2]
        args, _, _, values = inspect.getargvalues(frame)
        self.log.info('building cocoa.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
        if len(button1) <= 0 or len(title) <= 0 or len(label) <= 0:
            self.log.warning('must provide values for (button1) and (title) and (label)')
            sys.exit(1)
        else:
            return self.displayCocoa(funct, args, values)


"""
.. py:class Notifier()
Used for displaying MacOSX notifications on platforms 6+.
"""
class Notifier():

	"""
	.. py:function __init__(self, notifier)
	Initialize the Notifier object.

	:para str notifier: Path to the notifier binary (/Applications/terminal-notifier.app/Contents/MacOS/terminal-notifier)
	"""
	def __init__(self, notifier):
		self.log = Logger('notifier')
		self.utils = Utils()
		self.notifier = notifier

	"""
	.. py:function notification(self, titile='', subtitle='', sound='default', group='', sender='', open='', execute='', message='')
	Used for building and running the notification subprocess.

	:param str title: Title of the notification
	:param str subtitle: Subtitle of the notification
	:param str sound: Sound to play from "Sound Preferences"
	:param str group: Group ID of notification
	:param str sender: Bundle identifier of sending application
	:param str open: URL to open on notification click
	:param str execute: Command to execute on notification click
	:param str message: Message of notification
	"""
	def notification(self, title = '', subtitle = '', sound = 'default', group = 'lux.info', sender = '', open = '', execute = '', message = ''):
		frame = inspect.currentframe()
		funct = inspect.getframeinfo(frame)[2]
		args, _, _, values = inspect.getargvalues(frame)
		self.log.info('building notifier.%s with arguments %s' % (funct, str([(i, values[i]) for i in args])))
		if len(title) <= 0:
			self.log.warning('must provide values for (title)')
			sys.exit(1)
		else:
			process = self.notifier
			for i in args[1:]:
				if len(values[i]) > 0:
					process = '%s -%s "%s"' % (process, i, values[i])
			self.log.info('displaying %s' % funct)
			self.utils.runProcess(process)


"""
.. py:class Settings()
Used to allow users to edit settings saved in _config.xml
"""
class Settings():

    """
    .. py:function __init__(self)
    Initialize the Settings object.
    """
    def __init__(self):
        self.log = Logger('settings')
        self.binaries = Binaries()

    """
    .. py:function editDownloadDir(self)
    Prompt the user to change the download directory.
    """
    def editDownloadDir(self):
        self.log.info('changing download dir')
        editProc = self.binaries.cocoa.fileselect(title = PROGRAM, label = 'Select where downloads should be saved by default...',
            select_only_directories = True, with_directory = self.binaries.config.getDownloadDir())
        if len(editProc) > 0:
            self.binaries.config.editDownloadDir(editProc[0])
            self.log.info('change of download dir successful')
            self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Changed Download Directory', sender = self.binaries.sender, 
                message = editProc[0], sound = 'Purr')

    """
    .. py:function editVideoOpt(self)
    Prompt the user to change the default video format.
    """
    def editVideoOpt(self):
        self.log.info('changing video opt')
        videoFormats = {'FLV 360p':'34', 'WebM 480p':'44', 'MP4 720p':'22', '[3D] WebM 720p':'102', '[3D] MP4 360p':'82', 
            '3GP 144p':'17', 'MP4 360p':'18', '[3D] MP4 240p':'83', '3GP 240p':'36', 'MP4 1080p':'37', 'WebM 720p':'45', 
            '[3D] WebM 360p':'100', 'WebM 1080p':'46', 'FLV 240p':'5', 'FLV 480p':'35', '[3D] MP4 520p':'85', '[3D] MP4 720p':'84', 
            'FLV 270p':'6', 'WebM 360p':'43'}
        editProc = self.binaries.cocoa.dropdown(title = PROGRAM, label = 'Select your desired video download format...',
            button1 = 'Select', items = videoFormats.keys(), height = '130', string_output = True, button2 = 'Revert to Default')
        if 'select' in editProc[0].lower():
            self.binaries.config.editVideoOpt(videoFormats[editProc[1]])
            self.log.info('change of video opt successful')
            self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Changed Preferred Video Format', sender = self.binaries.sender,
                message = editProc[1], sound = 'Purr')
        else:
            self.binaries.config.editVideoOpt('', default = True)
            self.log.info('reset video opt to default')
            self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Changed Preferred Video Format', sender = self.binaries.sender,
                message = 'BEST POSSIBLE', sound = 'Purr')

    """
    .. py:function editAudioOpt(self)
    Prompt the user to change the default audio format.
    """
    def editAudioOpt(self):
        self.log.info('changing audio opt')
        audioFormats = ['.mp3', '.wav', '.ogg', '.m4a', '.wma']
        editProc = self.binaries.cocoa.dropdown(title = PROGRAM, label = 'Select your desired audio download format...',
            button1 = 'Select', items = audioFormats, height = '130', string_output = True, button2 = 'Revert to Default')
        if 'select' in editProc[0].lower():
            self.binaries.config.editAudioOpt(editProc[1])
            self.log.info('change of audio opt successful')
            self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Changed Preferred Audio Format', sender = self.binaries.sender,
                message = editProc[1], sound = 'Purr')
        else:
            self.binaries.config.editAudioOpt('', default = True)
            self.log.info('reset audio opt to default')
            self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Changed Preferred Audio Format', sender = self.binaries.sender,
                message = '%s (Default)' % self.binaries.config.getAudioOpt(), sound = 'Purr')

    """
    .. py:function toggleProgressBar(self)
    Toggle the progress bar between True and False.
    """
    def toggleProgressBar(self):
        self.log.info('toggling progress bar to %s' % str(not self.binaries.config.getProgressBar()))
        self.binaries.config.toggleProgressBar()
        self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Toggled Progress Bar', sender = self.binaries.sender,
            message = 'Progress Bar is now %s' % ('ON' if self.binaries.config.getProgressBar() else 'OFF'), sound = 'Purr')

    """
    .. py:function displayAbout(self)
    Display the program's about text in a cocoa textbox.
    """
    def displayAbout(self):
        self.log.info('displaying about textbox')
        self.binaries.cocoa.textbox(title = PROGRAM, label = 'Luxinate v%sr%s About' % (VERSION, RELEASE), text = self.binaries.config.getAbout(),
            button1 = 'Ok')

    """
    .. py:function resetToDefaults(self)
    Prompt the user to reset all settings of Luxinate's config to default.
    """
    def resetToDefaults(self):
        self.log.info('resetting _config\'s current state to defaults')
        editProc = self.binaries.cocoa.msgbox(title = PROGRAM, text = 'Resetting Luxinate to Default Settings...', button1 = 'Yes', button2 = 'No', 
            informative_text = 'Are you sure you want to continue?')
        if int(editProc[0]) == 1:
            self.binaries.config.editDownloadDir('', default = True)
            self.binaries.config.editVideoOpt('', default = True)
            self.binaries.config.editAudioOpt('', default = True)
            while not self.binaries.config.getProgressBar():
                self.binaries.config.toggleProgressBar()
            self.binaries.config.clearHistory()
            self.log.info('reset successful')
            self.binaries.notifier.notification(title = PROGRAM, subtitle = 'Luxinate Reset to Defaults', sender = self.binaries.sender,
                message = 'Reset Successful', sound = 'Purr')


i = Luxinate()
i.default('https://soundcloud.com/dubstep/arkasia-gravity')
j = Download()
j.defaultAudio()



