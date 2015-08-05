#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2015 Ritashugisha
# MIT License. <http://opensource.org/licenses/MIT>

"""
history

.. module:: history
    :platform: Windows, Linux, MacOSX
    :synopsis:
    :created: 2015-06-13 14:35:09
    :modified: 2015-06-24 11:01:29
.. moduleauthor:: ritashugisha (ritashugisha@gmail.com)

"""

import os
import ast
import json
import time
import datetime
import webbrowser

from utils import MetaSingleton, MetaSerializable, MetaLogged, MetaGlobalAccess


class History(
    MetaSingleton.Singleton, MetaSerializable.Serializable,
    MetaLogged.Logged, MetaGlobalAccess.GlobalAccess,
    object
):
    # FIXME: Fix history entries to be based of models from model.py

    def __init__(self):
        self.storage = os.path.join(
            self._global.ab.workflow_data, 'history.json'
        )
        if not os.path.exists(self.storage) or \
                len(open(self.storage, 'rb').read()) <= 0 or \
                self._default_changed():
            self.save(self.storage, self._global.history_defaults)
        self.load(self.storage)

    def _default_changed(self):
        self.load(self.storage)
        return set(self.history.keys()) != \
            set(self._global.history_defaults.keys()) or \
            set([type(i).__name__ for i in self.history.values()]) != \
            set([
                type(i).__name__
                for i in self._global.history_defaults.values()
            ])

    def load(self, path):
        self.history = json.load(open(path, 'rb'))

    def save(self, path, data):
        json.dump(data, open(path, 'wb'))
        self.load(path)

    def __getstate__(self):
        return {
            'storage': self.storage
        }

    def add(self, mod):
        # TODO: shrink amount of information stored by history entries
        if mod.info['display_id'] not in self.history['items'].keys():
            self.history['items'][mod.info['display_id']] = \
                self._global._merge_dicts(
                    dict([
                        (k, v,)
                        for (k, v,) in mod.info.iteritems()
                        if k not in self._global.history_mod_item_blacklist
                    ]),
                    {'downloaded': time.time()}
                )
            self.history['count'] += 1
        else:
            self.history['items'][mod.info['display_id']]['downloaded'] = \
                time.time()
        self.save(self.storage, self.history)

    def scriptfilter(self, query=None):
        # TODO: Better way to handle passing arguents with data
        _filter = self._global.ab.wrapper('scriptfilter')
        entries = []
        for (vid, entry,) in self.history['items'].iteritems():
            if query:
                if query.lower() in entry['title'].lower() or \
                        query.lower() in entry['uploader'].lower():
                    entries.append(entry)
            else:
                entries.append(entry)
        if len(self.history['items']) > 0:
            if len(entries) > 0:
                _filter.add(
                    title='Clear History',
                    subtitle='Remove all {} history entries'.format(
                        len(entries)
                    ),
                    arg=unicode({
                        'action': 'clear',
                        'entries': [i['display_id'] for i in entries]
                    }),
                    icon=self._global.icons['delete']
                )
                for entry in sorted(entries, key=lambda x: x['downloaded']):
                    _filter.add(
                        title=entry['title'],
                        subtitle=entry['uploader'],
                        arg=unicode({
                            'action': 'open',
                            'entries': [entry['webpage_url']]
                        }),
                        icon=self._global.icons['entry']
                    )
            else:
                _filter.add(
                    title='No Matching Entries',
                    subtitle='"{}" doesnt match any history entries'.format(
                        query
                    ),
                    arg=None,
                    icon=self._global.icons['x']
                )
        else:
            _filter.add(
                title='No History',
                subtitle='You have no history entries',
                arg=None,
                icon=self._global.icons['x']
            )
        return _filter

    def handler(self, query):
        if query['action'] == 'clear':
            if len(query['entries']) > 0:
                for entry in query['entries']:
                    if entry in self.history['items'].keys():
                        del self.history['items'][entry]
                    self.history['count'] -= 1
                self.save(self.storage, self.history)
                self._global.tn_client.notify(
                    title='{} History'.format(self._global.module_name),
                    message='Removed {} history entries'.format(
                        len(query['entries'])
                    ),
                    sender=self._global.notify_sender,
                    group=self._global.notify_group
                )
        elif query['action'] == 'open':
            for entry in query['entries']:
                webbrowser.open(entry)
