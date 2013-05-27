#!/usr/bin/env python
# Added by Chaobin Tang <cbtchn@gmail.com>
from datetime import datetime
from BeautifulSoup import BeautifulSoup

import requests


Config = {
    'url_channels': 'http://tv.cntv.cn/epg',
    'url_schedule':  'http://tv.cntv.cn/index.php?action=epg-list&date=%(date_str)s&channel=%(channel)s'
}

class Schedule(object):

    def __init__(self, channel_name):
        self.channel = channel_name

    def on_date(self, date_str):
        url_feed = {
            'date_str': date_str,
            'channel': self.channel
        }
        url = Config['url_schedule'] % url_feed
        response = requests.get(url)
        print response

class Channel(dict):

    def __init__(self, name, *args):
        self.name = name
        dict.__init__(self, *args)
        self['schedule'] = None

    def __getitem__(self, key):
        if self.schedule is None:
            # lazy load and cache the schedule
            self.set_schedule()
        return dict.__getitem__(self, key)

    def set_schedule(self):
        schedule = Schedule(self.name)
        dict.__setitem__(self, 'schedule', schedule)

    def __getattr__(self, attr):
        if not attr in self.keys():
            raise KeyError('Channel does not have `%s` attribute' % attr)
        return self[attr]

class Channels(dict):

    def __init__(self, *args):
        # init with keys, and set all values to None
        dict.__init__(self, self.channels_from_cntv())

    def __getitem__(self, channel_name):
        schedule = dict.__getitem__(self, channel_name)
        if schedule is None:
            # get schedule
            return None
        return schedule

    def __setitem__(self, channel_name, schedule):
        if not isinstance(schedule, Schedule):
            raise TypeError("Value must be an instance of Schedule")
        dict.__setitem__(self, channel_name, schedule)

    def channels_from_cntv(self):
        response = requests.get(Config['url_channels'])
        soup = BeautifulSoup(response.text)
        # processing part-of-the-doc is much faster
        body = soup.find('div', {'class': 'md_left'})
        channel_links = body.findAll('a', {'class': 'channel'})
        for link in channel_links:
            channel = Channel(link['rel'], link.attrMap)
            yield (channel['rel'], channel)