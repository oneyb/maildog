#!/usr/bin/env python3

import unittest
import sys
sys.path.append('../..')

import maildog as md
import config.config as cfg


class TestRenderTemplates(unittest.TestCase):
    """
    Make sure the templates render as expected
    """
    msg = md.Mail()
    rulesets = md.rulesets.get_rulesets(cfg.RULESET_FILE_PATTERN,
                                        cfg.REPLY_RULESETS_DIR)

    def test_render_templates(self):
        for ruleset in self.rulesets:
            self.msg.ruleset = ruleset
        self.msg.render_template(cfg.REPLY_TEMPLATE_DIR)
        self.assertIsInstance(self.msg.reply_message, str)
