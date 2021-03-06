#!/usr/bin/env python3

import sys, pdb
import smtplib
import logging

sys.path.append('../..')
from maildog import rulesets, mail
import config.config as cfg


logging.basicConfig(filename='maildoglog.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


mails = mail.get_new_emails(cfg)
if not mails:
    # nothing to do, go sleep
    sys.exit(0)

rulesets_list = rulesets.get_rulesets('csv', cfg.REPLY_RULESETS_DIR)


for msg in mails:

    msg.detect_language()
    msg.analyze_text()
    msg.extract_info_from_tags()
    msg.choose_ruleset(rulesets_list)

    if msg.ruleset:
        msg.render_template(cfg.REPLY_TEMPLATE_DIR)
        msg.reply_message = msg.compose_reply(cfg.REPLY_DATA_DIR)
        msg.reply = True
    else:
        logging.debug('Email needs attention: [%s] %s' %
                      (msg.uid, msg.subject))
        msg.reply_to = [cfg.MAILDOG_OWNER_EMAIL]
        msg.reply_message = msg.compose_notify_owner(rulesets_list,
                                                     cfg.MAILDOG_OWNER_EMAIL)


# Log in to email account and send mails
with smtplib.SMTP(cfg.SMTP_SERVER, cfg.SMTP_PORT) as send_server:
    send_server.ehlo()
    send_server.starttls()
    send_server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
    for msg in mails:
        msg.send_result = send_server.sendmail(msg.fro, msg.reply_to,
                                               msg.reply_message.as_string())
        print(msg.send_result)


# copy and delete if successfully answered, otherwise notify the owner
mail.copy_to_sent_and_mark_deleted(mails, cfg)
# # If you prefer to keep a clean inbox
# mail.delete_answered_emails(mails, cfg)
