#!/usr/bin/env python3

# Configure the program by setting some variables.
import os
MAILDOG_OWNER_EMAIL = 'iam@example.com'
MAILDOG_EMAIL = 'ur@example.com'
MAILDOG_EMAIL_PASSWORD = 'somethingcompllicated, but in plain text...'
IMAP_SERVER = 'imap.example.com'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
MAILDOG_SSL = True

MAILDOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPLY_DATA_DIR = os.path.join(MAILDOG_DIR, 'reply_data')
REPLY_RULESETS_DIR = os.path.join(MAILDOG_DIR, 'reply_rulesets')
REPLY_TEMPLATE_DIR = os.path.join(MAILDOG_DIR, 'reply_templates')
RULESET_FILE_PATTERN = '.'
TEMPLATE_FILE_PATTERN = '.j2'
