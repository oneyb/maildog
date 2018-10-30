#!/usr/bin/env python3

import unittest
import sys
sys.path.append('../..')

import imapclient
import maildog as md


class TestEmailConfig(unittest.TestCase):
    '''
    Test email configuration
    '''
    import config.config as cfg

    def test_config_names(self):
        expected_config_names = [
            'MAILDOG_OWNER_EMAIL',
            'MAILDOG_EMAIL',
            'MAILDOG_EMAIL_PASSWORD',
            'IMAP_SERVER',
            'SMTP_SERVER',
            'SMTP_PORT',
            'MAILDOG_DIR',
            'REPLY_DATA_DIR',
            'REPLY_RULESETS_DIR',
            'REPLY_TEMPLATE_DIR',
            'RULESET_FILE_PATTERN',
            'MAILDOG_SSL'
        ]
        if hasattr(self.cfg, "__loader__"):
            found = dir(self.cfg)

        for x in expected_config_names:
            self.assertIn(x, found)

    def test_select_inbox(self):
        with imapclient.IMAPClient(self.cfg.IMAP_SERVER,
                                   ssl=self.cfg.MAILDOG_SSL) as server:
            _ = server.login(self.cfg.MAILDOG_EMAIL,
                             self.cfg.MAILDOG_EMAIL_PASSWORD)
            res = server.select_folder('INBOX')
            self.assertIsInstance(res, dict)
