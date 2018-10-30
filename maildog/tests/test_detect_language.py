#!/usr/bin/env python3

import sys
import unittest

sys.path.append('../..')
import maildog as md


class TestDetectLanguage(unittest.TestCase):
    """
    Make sure the email language is detected correctly
    """

    msg = md.Mail()

    def test_detect_english(self):
        self.msg.body = 'Some test with punctuation and contents.'
        self.msg.subject = 'important email'
        self.msg.detect_language()
        self.assertEqual(self.msg.language, 'english')

    def test_detect_german(self):
        self.msg.body = 'Ein normaler Text mit einigen Informationen.'
        self.msg.subject = 'Hallo'
        self.msg.detect_language()
        self.assertEqual(self.msg.language, 'german')

    # def test_detect_italian(self):
    #     # # TODO: the following text fails
    #     # self.msg.body = 'Cosa posso fare. Vuoi partecipare. Prego! Ciao!'
    #     # # This one is less difficult, sometimes english, sometimes italian.
    #     self.msg.body = "Posso essere d'aiuto? Non può andare a finire bene!"
    #     self.msg.subject = 'Ciao'
    #     self.msg.detect_language()
    #     self.assertEqual(self.msg.language, 'italian')

    def test_detect_french(self):
        self.msg.body = 'Je peux vous aider ?'
        self.msg.subject = 'Bonjour'
        self.msg.detect_language()
        self.assertEqual(self.msg.language, 'french')
