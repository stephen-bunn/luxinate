#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import json
import locale
import urllib
import utils

# Format search of YouTube's gdata for Alfred 2
#
# @param query Query to search YouTube's gdata
# @param maxResults = 0
# @param showViews = False
def searchVideos(query, maxResults = 0, showViews = False):
    def configure():
        if showViews:
            locale.setlocale(locale.LC_ALL, LOCALE)
    def toString(seconds):
        hours = seconds / 3600
        minutes = (seconds % 3600) / 60
        seconds = seconds % 3600 % 60
        result = ''
        if hours > 0:
            result = '%sh' % hours
        if minutes > 0:
            if hours > 0:
                result = '%s ' % result
            result = '%s%sm' % (result, minutes)
        if seconds > 0:
            if hours > 0 and minutes == 0 or minutes > 0:
                result = '%s ' % result
            result = '%s%ss' % (result, seconds)
        return result
    configure()
    urlQuery = 'https://gdata.youtube.com/feeds/api/videos?v=2&alt=jsonc&q=%s&orderby=relevance' % query
    if maxResults >= 1 and maxResults <= 50:
        urlQuery = '%s&max-results=%s' % (urlQuery, maxResults)
    content = json.loads(urllib.urlopen(urlQuery).read())
    if 'data' in content and 'items' in content['data']:
        items = content['data']['items']
        f = utils.Feedback()
        for i in items:
            videoId = i['id']
            if videoId is not None:
                videoTitle = i['title']
                videoSubtitle = 'by %s [%s]' % (i['uploader'], toString(i['duration']))
                if showViews:
                    videoViewCount = i['viewCount']
                    videoViewWord = 'view'
                    if videoViewCount is not 1:
                        videoViewWord = 'views'
                    videoSubtitle = '%s [%s %s]' % (videoSubtitle, locale.format('%d', videoViewCount, grouping = True), videoViewWord)
                f.add_item(videoTitle, videoSubtitle, 'http://www.youtube.com/watch?v=%s' % videoId, '', '', 'Icons/_download.png')           
    else:
        f = utils.Feedback()
        f.add_item('No results', 'No results were found', '', '', '', 'Icons/_x.png')
    return f
