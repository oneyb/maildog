#!/usr/bin/env python3

import sys

sys.path.append('../..')
import maildog as md

msg = md.Mail()

def test_detect_english_name():
    msg.body = """I have just taken a course and am interested to come.
    Do I have to register? \r\nThanks, \r\nMike"""
    msg.subject = 'Hi everybody!'
    msg.detect_language()
    msg.analyze_text()
    msg.extract_info_from_tags()
    print(msg.info)
    print(msg._doc)


test_detect_english_name()
