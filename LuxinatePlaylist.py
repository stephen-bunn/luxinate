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
import urllib, urlparse
from xml.dom import minidom
import utils, soundcloud

# Validate query URL and format Alfred feed
#
# @param query URL to be validated and passed as next {query}
def process(query):
    f = utils.Feedback()
    try:
        if utils.validateUrl(query) and 'soundcloud' in utils.checkDomain(query) and 'sets' in urlparse.urlparse(query).path.split('/')[2].lower():
            f.add_item('Download Playlist Audio', query, "{'node':%s,'url':\'%s\'}" % ('2', query), '', '', 'Icons/_audio.png')
        elif utils.validateUrl(query) and 'youtube' in utils.checkDomain(query) and 'playlist' in urlparse.urlparse(query).path.lower():
            f.add_item('Download Playlist Video', query, "{'node':%s,'url':\'%s\'}" % ('1', query), '', '', 'Icons/_video.png')
            f.add_item('Download Playlist Audio', query, "{'node':%s,'url':\'%s\'}" % ('2', query), '', '', 'Icons/_audio.png')
        else:
            f.add_item('No Download', 'Invalid playlist URL', '', '', '', 'Icons/_x.png')
        print f
    except ValueError:
        client = soundcloud.Client(client_id = utils.SOUNDCLOUD_API)
        playlistsSoundCloud = client.get('/playlists', q = query, limit = 9)
        playlistsYouTube = []
        urlValid = 'https://gdata.youtube.com/feeds/api/playlists/snippets?v=2&q=%s&max-results=9' % query
        for i in minidom.parseString(urllib.urlopen(urlValid).read()).getElementsByTagName('entry'):
            newList = {}
            domTitle = i.getElementsByTagName('link')[1].getAttribute('href')
            domDescription = i.getElementsByTagName('summary')[0].firstChild
            domName = i.getElementsByTagName('author')[0].firstChild.firstChild.nodeValue
            if domDescription is not None:
                domDescription = domDescription.data
            newList['title'] = domTitle
            newList['description'] = domDescription
            newList['name'] = domName
            playlistsYouTube.append(newList)
        increment = 0
        while increment < len(playlistsYouTube):
            try:
                f.add_item(playlistsYouTube[increment]['name'], playlistsYouTube[increment]['description'],
                playlistsYouTube[increment]['title'], '', '', 'Icons/_youtube.png')
            except IndexError:
                pass
            try:
                f.add_item(playlistsSoundCloud[increment].title, playlistsSoundCloud[increment].description,
                playlistsSoundCloud[increment].permalink_url, '', '', 'Icons/_soundcloud.png')
            except IndexError:
                pass
            increment += 1
        print f

# Download each video in the validated playlist URL
#
# @param url URL to playlist
def downloadPlaylistVideo(url):
    utils.writeHistory(url)
    if utils.FORMAT_VIDEO:
        downloadCmd = 'cd %s;%s -citf %s %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, utils.FORMAT_VIDEO, url)
    else:
        downloadCmd = 'cd %s;%s -it %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.PROGRESS:
        utils.writeTemp(url)
        downloadCmd = '%s --newline' % downloadCmd
        utils.spawnProgressBar()
        proc = utils.runProgressBarDownload(downloadCmd)
    else:
        utils.displayNotification(utils.TITLE, url, '► Downloading Playlist\'s Video', 'open %s' % utils.DOWNLOAD)    
        proc = utils.runProcess(downloadCmd)
    utils.killProgressBar()
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    utils.sendDiagnostics('downloadPlaylistVideo', downloadCmd, '', proc)

# Download each audio in the validated playlist URL
#
# @param url URL to playlist    
def downloadPlaylistAudio(url):
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
                utils.runProgressBarConvert(convertCmd, quitFilter = False)
            else:
                utils.runProcess(convertCmd)
    passConvert = False
    utils.writeHistory(url)
    if 'soundcloud' in utils.checkDomain(url):
            passConvert = True
            convertCmd = ''
    if not passConvert:
        downloadCmd = 'mkdir %s;cd %s;%s -cit %s' % (utils.TEMPDIR, utils.TEMPDIR, utils.YOUTUBE_DL, url)
    else:
        downloadCmd = 'cd %s;%s -cit %s' % (utils.DOWNLOAD, utils.YOUTUBE_DL, url)
    if utils.PROGRESS:
        utils.spawnProgressBar()
        utils.writeTemp(url)
        downloadCmd = '%s --newline' % downloadCmd
        if not passConvert:
            utils.runProgressBarDownload(downloadCmd, quitFilter = False)
            convertFiles(progressBar = True)
            proc = ''
        else:
            utils.runProgressBarDownload(downloadCmd)
            proc = ''
    else:
        utils.displayNotification(utils.TITLE, url, '► Downloading Playlist\'s Audio', 'open %s' % utils.DOWNLOAD)
        if not passConvert:
            proc = utils.runProcess(downloadCmd)
            convertFiles()
        else:
            proc = utils.runProcess(downloadCmd)
    utils.killProgressBar()
    utils.displayNotification(utils.TITLE, url, 'Download Complete', 'open %s' % utils.DOWNLOAD)
    os.system('rm -rf %s' % utils.TEMPDIR)
    utils.sendDiagnostics('downloadPlaylistAudio', downloadCmd, 'Playlist_Download', proc)
    
# Parse the selected option to the correct function
#
# @param query Dictonary string with download information     
def parseQuery(query):
    try:
        q = ast.literal_eval(query)
        if q['node'] == 1:
            downloadPlaylistVideo(q['url'])
        else:
           downloadPlaylistAudio(q['url'])
    except UnicodeDecodeError:
        pass
    except:
        utils.runProcess('osascript -e \'tell application \"Alfred 2\" to search \"luxplaylist ► \" & \"%s\"\'' % query)
                          