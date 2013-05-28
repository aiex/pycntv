#!/usr/bin/env python
# Added by Chaobin Tang <cbtchn@gmail.com>
from calendar import Calendar
from datetime import date, datetime
from collections import namedtuple
import random

from BeautifulSoup import BeautifulSoup
import requests


class CNTV(object):

    Config = {
        'url_channels': 'http://tv.cntv.cn/epg',
        'url_schedule': (
            'http://tv.cntv.cn/index.php?action=epg-list&date=%(date_str)s&channel=%(channel)s&mode='
            )
    }

    FORMAT_DATE = '%Y-%m-%d'
    FORMAT_TIME = '%H:%M'
    NotFound = '0'
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0',
        'Mozilla/5.0 (Windows NT 5.1; rv:20.0) Gecko/20100101 Firefox/20.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
    ]
    HEADERS = {
        'Accept': '*/*',
        'Accept-Charset': 'UTF-8,*;q=0.5',
        'Accept-Language': 'en-US,en;q=0.8,fr;q=0.6',
        'Host': 'tv.cntv.cn',
        'Referer': 'http://tv.cntv.cn/epg',
        'X-Requested-With': 'XMLHttpRequest',
    }

    def program_time_from_date_and_time_str(self, str_date, str_time):
        separator = ' '
        return datetime.strptime(
            separator.join([str_date, str_time]),
            separator.join([self.FORMAT_DATE, self.FORMAT_TIME])
        )

    def GET(self, url, **kwargs):
        random_agent = random.choice(self.USER_AGENTS)
        headers = self.HEADERS
        headers['User-Agent'] = random_agent
        response = requests.get(
            url,
            headers = headers,
            **kwargs
        )
        return response

    def iterchannels(self):
        response = self.GET(self.Config['url_channels'])
        soup = BeautifulSoup(response.text)
        # Processing part-of-the-doc is much faster
        body = soup.find('div', {'class': 'md_left'})
        channel_links = body.findAll('a', {'class': 'channel'})
        for link in channel_links:
            channel = Channel(link.attrMap)
            yield (channel['rel'], channel)

    def iterprograms(self, _date, channel_rel):
        '''Grab the schedule on a specified date.

        :param _date: datetime.date object
        :param channel_rel: channel code names.
            e.g., ``'cctv1'``

        :return: Returns a generator object.
        '''
        date_str = _date.strftime(self.FORMAT_DATE)
        url_feed = {
            'date_str': date_str,
            'channel': channel_rel
        }
        url = self.Config['url_schedule'] % url_feed
        response = self.GET(url)

        if response.text == self.NotFound:
            raise StopIteration('No programs found')
        else:
            soup = BeautifulSoup(response.text)
            for dd in soup.findAll('dd'):
                program = self.program_from_dd(date_str, dd)
                if program is None:
                    continue
                else:
                    yield (program.time, program)

    def program_from_dd(self, date_str, dd):
        '''Parsing program info from 'dd` node.
        
        Do the xpath parsing and information serialization
        from arbitrary string including program time stamp
        generation from string and format. This function should
        be tolerant.

        :param date_str: date string representing the the date of schedule.
        :param dd: the child node found in a soup object.

        :return: Returns Program instance on success.
            Returns None on any error, to indicate that the caller
            should ignore this time of parse and continue its iteration.
        '''
        program_details_str = None

        def decide():
            Unknown = when_details_is_missing
            has_links = ( len(dd.findChildren('a')) > 0)
            if has_links:
                return when_details_is_linked
            else:
                return when_details_is_plain_text
            return Unknown

        def when_details_is_missing():
            return None

        def when_details_is_linked():
            node_playback = node_program = None
            links = dd.findChildren('a')
            # Programs already aired will have a link
            # to the playback URL, resulting in two links
            # in the dd node.
            if len(links) > 1:
                node_playback, node_program = links
            else:
                try:
                    node_program = links[0]
                except IndexError:
                    return None
            return node_program.text

        def when_details_is_plain_text():
            return dd.text.strip()

        situation = decide()
        program_details_str = situation()

        if program_details_str is None:
            return None

        program_details_splitted = program_details_str.split()
        program_time_str = program_details_splitted.pop(0)
        program_time = self.program_time_from_date_and_time_str(
            date_str, program_time_str
        )
        program_name = ' '.join(program_details_splitted)
        program = Program(
            time=program_time,
            name=program_name
        )
        return program

Program = namedtuple('Program', 'time, name')

class Programs(dict, CNTV):

    def __init__(self, channel, _date, *args):
        self.channel = channel
        self._date = _date

        if args:
            dict.__init__(self, *args)
        else:
            dict.__init__(self, self.iterprograms(self._date, self.channel))

class Schedule(Calendar):

    def __init__(self, channel_name, firstweekday=0):
        self.today = date.today()
        self.channel = channel_name
        Calendar.__init__(self, firstweekday)

    def iterweeklyschedules(self):
        monthdates = self.itermonthdates(
            self.today.year, self.today.month
        )
        for _date in monthdates:
            if _date < self.today:
                continue
            else:
                programs = Programs(self.channel, _date)
                yield programs

class Channel(dict):

    def __init__(self, *args):
        dict.__init__(self, *args)
        self['schedule'] = None

    def __getitem__(self, key):
        if self.schedule is None:
            # Lazy load and cache the schedule
            self.set_schedule()
        return dict.__getitem__(self, key)

    def set_schedule(self):
        schedule = Schedule(self.rel)
        dict.__setitem__(self, 'schedule', schedule)

    def __getattr__(self, attr):
        return dict.__getitem__(self, attr)

class Channels(dict, CNTV):

    def __init__(self, *args):
        if args:
            # e.g., Load from a cached source
            dict.__init__(self, *args)
        else:
            dict.__init__(self, self.iterchannels())

    def __setitem__(self, channel_name, schedule):
        if not isinstance(schedule, Schedule):
            raise TypeError("Value must be an instance of Schedule")
        dict.__setitem__(self, channel_name, schedule)
        