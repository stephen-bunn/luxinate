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

import os, ast
import urllib, urllib2, urlparse, json
from xml.dom import minidom
import utils, soundcloud

def process(query):
    f = utils.Feedback()
    try:
        utils.validateUrl(query)
        if 'www' in urlparse.urlparse(query).netloc[0:3].lower():
            urlDomain = urlparse.urlparse(query).netloc.split('.', 2)[1].lower()
        else:
            urlDomain = urlparse.urlparse(query).netloc.split('.', 2)[0].lower()
        if 'youtube' in urlDomain:
            if 'user' in urlparse.urlparse(query).path.split('/')[1].lower() or 'channel' in urlparse.urlparse(query).path.split('/')[1].lower():
                f.add_item('Download Video', 'Download all uploads as video', "{'node':1,'url':\'%s\'}" % query, '', '', 'Icons/_user.png')
                f.add_item('Download Audio', 'Download all uploads as audio', "{'node':2,'url':\'%s\'}" % query, '', '', 'Icons/_user.png')
            else:
                f.add_item('No Results', 'No results were found', '', '', '', 'Icons/_x.png')
        elif 'soundcloud' in urlDomain:
            if len(urlparse.urlparse(query).path.split('/')[1:]) == 1:
                f.add_item('Download Audio', 'Download all uploads as audio', "{'node':2,'url':\'%s\'}" % query, '', '', 'Icons/_user.png')
            else:
                f.add_item('No Results', 'No results were found', '', '', '', 'Icons/_x.png')
        else:
            f.add_item('No Results', 'No results were found', '', '', '', 'Icons/_x.png')
        print f
    except ValueError:
        client = soundcloud.Client(client_id = utils.SOUNDCLOUD_API)
        usersSoundCloud = client.get('/users', q = query, limit = 9)
        usersYouTube = []
        urlValid = 'https://gdata.youtube.com/feeds/api/channels?v=2&q=%s&max-results=9' % query
        for i in minidom.parseString(urllib.urlopen(urlValid).read()).getElementsByTagName('entry'):
            newList = {}
            domTitle = i.getElementsByTagName('uri')[0].firstChild.nodeValue.split('/')[-1]
            domDescription = i.getElementsByTagName('summary')[0].firstChild
            domName = i.getElementsByTagName('author')[0].firstChild.firstChild.nodeValue
            if domDescription is not None:
                domDescription = domDescription.data
            newList['title'] = domTitle
            newList['description'] = domDescription
            newList['name'] = domName
            usersYouTube.append(newList)
        increment = 0
        while increment < len(usersYouTube):
            try:
                f.add_item(usersYouTube[increment]['name'], usersYouTube[increment]['description'], 
                "http://www.youtube.com/user/%s" % usersYouTube[increment]['title'], '', '', 'Icons/_youtube.png')
            except IndexError:
                pass
            try:
                f.add_item(usersSoundCloud[increment].username, usersSoundCloud[increment].description, 
                usersSoundCloud[increment].permalink_url, '', '', 'Icons/_soundcloud.png')
            except IndexError:
                pass
            increment += 1
        print f
        
def getYouTubeResults(url):
    results = []
    allDone = False
    increment = 1
    while not allDone:
        gdata = urllib.urlopen(
        r'http://gdata.youtube.com/feeds/api/videos?start-index=%s&max-results=50&alt=json&orderby=published&author=%s' % (
        increment, urlparse.urlparse(url).path.split('/')[2]))
        try:
            response = json.load(gdata)
            gdata.close()
            returnedVideos = response['feed']['entry']
            for video in returnedVideos:
                results.append(video['link'][0]['href'])
            increment += 50
            if len(returnedVideos) < 50:
                allDone = True
        except:
            allDone = True
    return results

def getSoundCloudResults(url):
    results = []
    client = soundcloud.Client(client_id = utils.SOUNDCLOUD_API)
    userId = json.loads(urllib2.urlopen('http://api.soundcloud.com/resolve.json?url=%s&client_id=%s' % (url, utils.SOUNDCLOUD_API)).read())['id']
    for i in client.get('/users/%s/tracks' % userId):
        results.append(i.permalink_url)
    return results

def downloadUserVideo(url):
    results = getYouTubeResults(url)
    if not utils.PROGRESS:
        utils.displayNotification(utils.TITLE, url, '► Downloading %s\'s Video' % urlparse.urlparse(url).path.split('/')[2], 
        'open %s' % utils.DOWNLOAD)
    else:
        utils.spawnProgressBar()
    for i in results:
        i = utils.formatUrl(i)
        utils.writeHistory(i)
        if utils.FORMAT_VIDEO:
            downloadCmd = 'cd %s;%s -citf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, i)
        else:
            downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, i)
        if utils.PROGRESS:
            utils.writeTemp(i)
            downloadCmd = '%s --newline' % downloadCmd
            proc = utils.runProgressBarDownload(downloadCmd, quitFilter = False, spawnKill = False)
        else:    
            proc = utils.runProcess(downloadCmd)
    utils.killProgressBar()
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadPlaylistVideo', '', '', proc)

def downloadUserAudio(url):
    def convertFiles(progressBar = False):
        for i in os.listdir(utils.TEMPDIR):
            mediaFile = os.path.basename(i).split('.')[0]
            if utils.FORMAT_AUDIO:
                if utils.FORMAT_AUDIO == '.mp3':
                    convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces('%s%s' % (utils.TEMPDIR, utils.formatConsole(i))),
                    utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
                else:
                    convertCmd = '%s -y -i %s %s' % (utils.FFMPEG, utils.formatSpaces('%s%s' % (utils.TEMPDIR, utils.formatConsole(i))),
                    utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), utils.FORMAT_AUDIO))
            else:
                convertCmd = '%s -y -i %s -b:a 320k %s' % (utils.FFMPEG, utils.formatSpaces('%s%s' % (utils.TEMPDIR, utils.formatConsole(i))),
                utils.replaceExtension('%s%s' % (utils.DOWNLOAD, utils.formatConsole(utils.formatSpaces(mediaFile))), '.mp3'))
            if progressBar:
                utils.runProgressBarConvert(convertCmd)
            else:
                utils.runProcess(convertCmd)
    passConvert = False
    if 'soundcloud' in utils.checkDomain(url):
        passConvert = True
        results = getSoundCloudResults(url)
        convertCmd = ''
    elif 'youtube' in utils.checkDomain(url):
        results = getYouTubeResults(url)
    else:
        pass
    if not utils.PROGRESS:
        if passConvert:
            utils.displayNotification(utils.TITLE, url, '► Downloading %s\'s Audio' % urlparse.urlparse(url).path.split('/')[1], 
            'open %s' % utils.DOWNLOAD)
        else:
            utils.displayNotification(utils.TITLE, url, '► Downloading %s\'s Audio' % urlparse.urlparse(url).path.split('/')[2], 
            'open %s' % utils.DOWNLOAD)
    else:
        utils.spawnProgressBar()
    for i in results:
        i = utils.formatUrl(i)
        utils.writeHistory(i)
        if passConvert:
            downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, i)
        else:
            downloadCmd = 'mkdir %s;cd %s;%s -cit %s' % (utils.TEMPDIR, utils.TEMPDIR, utils.YOUTUBE_DL, i)
        if utils.PROGRESS:
            utils.writeTemp(url)
            downloadCmd = '%s --newline' % downloadCmd
            utils.runProgressBarDownload(downloadCmd, quitFilter = False, spawnKill = False)
            proc = ''
        else:
            proc = utils.runProcess(downloadCmd)
    if utils.PROGRESS:
        if not passConvert:
            convertFiles(progressBar = True)
    else:
        if not passConvert:
            convertFiles()
    utils.killProgressBar()
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    os.system('rm -rf %s' % utils.TEMPDIR)
    utils.sendDiagnostics('downloadPlaylistAudio', downloadCmd, 'Playlist_Download', proc)            

def parseQuery(query):
    try:
        q = ast.literal_eval(query)
        if q['node'] == 1:
            downloadUserVideo(q['url'])
        else:
            downloadUserAudio(q['url'])
    except UnicodeDecodeError:
        pass
    except:
        utils.runProcess('osascript -e \'tell application \"Alfred 2\" to search \"luxuser ► \" & \"%s\"\'' % query)


                    