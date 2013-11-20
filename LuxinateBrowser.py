#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import utils

def process(browser):
    osaCmd = "osascript -e 'tell application \"%s\" to get URL of every Tab of every Window'" % browser
    return utils.runProcess(osaCmd).replace('\n', '').split(', ')

def LuxinateBrowser(query, browser):
    feed = utils.Feedback()
    for i in process(browser):
        try:
            (mediaTitle, mediaFile) = utils.getMediaInfo(i)
            if utils.determineMediaType(mediaFile) == 1:
                q = "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('1',
                i, utils.formatDict(mediaTitle), utils.formatDict(mediaFile))
                feed.add_item(mediaTitle, i, q, '', '', 'Icons/_download.png')
            elif utils.determineMediaType(mediaFile) == 2:
                q = "{'node':%s,'url':\'%s\','title':\'%s\','file':\'%s\'}" % ('2',
                i, utils.formatDict(mediaTitle), utils.formatDict(mediaFile))
                feed.add_item(mediaTitle, i, q, '', '', 'Icons/_download.png')
        except ValueError:
            pass
            #feed.add_item('No download', 'Invalid URL %s' % i, '', '', '', 'Icons/_x.png')
    print feed
    
def openLuxDefault(query):
    osaCmd = 'osascript -e \'tell application "Alfred 2" to search "lux ► " & "' + query['url'] + '"\''
    utils.runProcess(osaCmd)
    