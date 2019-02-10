#!/usr/bin/env python3

import unittest
import sys
sys.path.append('../..')

import imapclient
import maildog as md


class TestEmailNotification(unittest.TestCase):
    '''
    Test email notifications
    '''
    import config.config as cfg

