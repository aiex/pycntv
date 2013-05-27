#!/usr/bin/env python
# Added by Chaobin Tang <cbtchn@gmail.com>
from BeautifulSoup import BeautifulSoup
from calendar import Calendar
from datetime import datetime
from collections import namedtuple

import requests


Config = {
    'url_channels': 'http://tv.cntv.cn/epg',
    'url_schedule': (
        'http://tv.cntv.cn/index.php?action=epg-list&date=%(date_str)s&channel=%(channel)s&mode='
        )
}

Program = namedtuple('Program', 'time', 'name')

class Schedule(Calendar):

    def __init__(self, channel_name, firstweekday=0):
        self.channel = channel_name
        Calendar.__init__(self, firstweekday)

    def on_date(self, date_str):
        url_feed = {
            'date_str': date_str,
            'channel': self.channel
        }
        url = Config['url_schedule'] % url_feed
        response = requests.get(url)

    def 

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
        return dict.__getitem__(self, attr)

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