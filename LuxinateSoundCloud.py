#!/usr/bin/env python
#-*- coding:UTF-8 -*-
#
# @author:  Ritashugisha
# @contact: ritashugisha@gmail.com

import utils
import soundcloud

def searchSounds(query):
    client = soundcloud.Client(client_id = utils.SOUNDCLOUD_API)
    f = utils.Feedback()
    tracks = client.get('/tracks', q = query, limit = 9)
    if not tracks:
        f.add_item('No results', 'No results were found', '', '', '', 'Icons/_x.png')
    else:
        for i in tracks:
            f.add_item(i.title, i.permalink, '%s{|lux|}%s{|lux|}%s' % (str(i.user_id), i.permalink, i.title), '', '', 'Icons/_download.png')
    print f
    
def buildUrl(query):
    client = soundcloud.Client(client_id = utils.SOUNDCLOUD_API)
    query = query.split('{|lux|}')
    userId = query[0]
    permalink = query[1]
    artist = client.get('/users/' + userId)
    return "http://www.soundcloud.com/" + artist.permalink + '/' + permalink
        