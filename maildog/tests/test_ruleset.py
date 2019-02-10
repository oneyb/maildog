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

    msg = md.Mail()

    def test_get_rulesets_configured(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        self.assertIsInstance(rulesets[0], tuple)
        self.assertIsInstance(rulesets, list)

    def test_get_rulesets_csv(self):
        rulesets = md.rulesets.get_rulesets('csv', cfg.REPLY_RULESETS_DIR)
        self.assertIsInstance(rulesets[0], tuple)
        self.assertIsInstance(rulesets, list)

    def test_get_rulesets_xlsx(self):
        # f = 'reply_rulesets/rulesets.xlsx'
        rulesets = md.rulesets.get_rulesets('xlsx', cfg.REPLY_RULESETS_DIR)
        # print( rulesets )
        self.assertIsInstance(rulesets[0], tuple)
        self.assertIsInstance(rulesets, list)

    def test_get_no_ruleset_for_english(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        self.msg.body = 'Some test with punctuation and contents.'
        self.msg.subject = 'important email'
        self.msg.fro = 'user@example.com'
        self.msg.detect_language()
        rulesets = [r for r in rulesets if r.language is not 'english']
        self.msg.analyze_text()
        self.msg.choose_ruleset(rulesets)
        self.assertIsNone(self.msg.ruleset)
        
    def test_get_no_ruleset_for_german(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        self.msg.body = 'Ich bin ein normaler Text mit einigen Informationen.'
        self.msg.subject = 'Hallo'
        self.msg.fro = 'user@example.com'
        self.msg.detect_language()
        rulesets = [r for r in rulesets if r.language is not 'german']
        self.msg.analyze_text()
        self.msg.choose_ruleset(rulesets)
        self.assertIsNone(self.msg.ruleset)

    def test_all_rulesets_disqualified(self):
        rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                            cfg.REPLY_RULESETS_DIR)
        self.msg.body = 'Some test with contents. Today or tomorrow.'
        self.msg.subject = 'important email'
        self.msg.fro = 'user@example.com'
        self.msg.detect_language()
        self.msg.analyze_text()
        self.msg.choose_ruleset(rulesets)
        self.assertIsNone(self.msg.ruleset)
