#!/usr/bin/env python
# Added by Chaobin Tang <cbtchn@gmail.com>
import unittest

import tv


class TVTest(unittest.TestCase):

    def setUp(self):
        self.channels = tv.Channels()

    def test_schedule(self):
        channel = self.channels['cctv5']
        for schedule in channel.schedule.iterweeklyschedules():
            for time, program in schedule.iteritems():
                print time, program.name

if __name__ == '__main__':
    unittest.main()