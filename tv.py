#!/usr/bin/env python
# Added by Chaobin Tang <cbtchn@gmail.com>
from datetime import datetime

import requests


class Schedule(object):
    pass

class Channels(dict):

    def __init__(self):
        # init with keys, and set all values to None
        keys = self.keys()
        dict.__init__(self, list(zip(keys, [None] * len(keys))))

    def __getitem__(self, channel_name):
        schedule = self[channel_name]
        if item is None:
            # get schedule
            pass
        return schedule

    def __setitem__(self, channel_name, schedule):
        if not isinstance(schedule, Schedule):
            raise TypeError("Value must be an instance of Schedule")
        self[channel_name] = schedule

    def keys(self):
        return range(5)
        if self.keys():
            return self.keys()
        