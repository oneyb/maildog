#!/usr/bin/env python3

import sys
import unittest

sys.path.append('../..')
import maildog as md


class TestExtractContents(unittest.TestCase):
    """
    Make sure the email language is detected correctly
    """

    msg = md.Mail()

    def test_detect_english_name(self):
        self.msg.body = """I have just taken a course and am interested to come. Do I have to register? \r\nThanks, \r\nMike"""
        self.msg.subject = 'Hi everybody!'
        self.msg.fro = 'mike.johnson@gmail.com'
        self.msg.detect_language()
        self.msg.analyze_text()
        self.msg.extract_info_from_tags()
        print(self.msg.info)
        print(self.msg._doc)
        self.assertEqual(self.msg.info['first_name'], ['mike'])


    def test_detect_german_name(self):
        self.msg.body = """Ich habe gerade einen Kurs gemacht und bin interessiert zu kommen. Muss ich mich da anmelden?\r\nLiebe Grüsse\r\nHeike Paur\n8001 Zürich"""
        self.msg.subject = 'Hallo zusammen'
        self.msg.fro = u'heike@gmail.com'
        self.msg.detect_language()
        self.msg.analyze_text()
        self.msg.extract_info_from_tags()
        print(self.msg.info)
        # print([(w.text, w.pos_) for w in msg._doc])
        self.assertEqual(self.msg.info['first_name'], ['heike'])

