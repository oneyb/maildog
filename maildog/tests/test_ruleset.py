#!/usr/bin/env python3

import unittest
import sys
sys.path.append('../..')

import maildog as md
import config.config as cfg


class TestRuleset(unittest.TestCase):

    """
    Make sure the rulesets work as expected
    """


    def test_get_rulesets_configured(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        self.assertIsInstance(rulesets[0], tuple)
        self.assertIsInstance(rulesets, list)

    def test_get_rulesets_csv(self):
        rulesets = md.rulesets.get_rulesets('csv', cfg.REPLY_RULESETS_DIR)
        self.assertIsInstance(rulesets[0], tuple)
        self.assertIsInstance(rulesets, list)

    def test_get_no_ruleset_for_english(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        msg = md.Mail()
        msg.body = 'Some test with punctuation and contents.'
        msg.subject = 'important email'
        msg.detect_language()
        rulesets = [r for r in rulesets if r.language is not 'english']
        msg.choose_ruleset(rulesets)
        self.assertIsNone(msg.ruleset)

    def test_get_no_ruleset_for_german(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        msg = md.Mail()
        msg.body = 'Ein normaler Text mit einigen Informationen.'
        msg.subject = 'Hallo'
        msg.detect_language()
        rulesets = [r for r in rulesets if r.language is not 'german']
        msg.choose_ruleset(rulesets)
        self.assertIsNone(msg.ruleset)

    def test_all_rulesets_disqualified(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        msg = md.Mail()
        msg.body = 'Some test with contents. Today or tomorrow.'
        msg.subject = 'important email'
        msg.detect_language()
        msg.choose_ruleset(rulesets)
        self.assertIsNone(msg.ruleset)
