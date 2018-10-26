#!/usr/bin/env python3
import sys, pdb

import imapclient
import smtplib
import pyzmail
import logging
# import time

from . import Mail


def get_new_emails(cfg):
    """
    1. Log in to the email server.
    2. Read ENVELOPE and BODY
    3. Put essentials together
    """

    print("Connecting")
    with imapclient.IMAPClient(cfg.IMAP_SERVER, ssl=True) as server:
        server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
        server.select_folder('INBOX')
        logging.debug('Connected. %s' % server.welcome)

        # Fetch all instruction emails.
        UIDs = server.search("UNANSWERED")
        # messages = server.fetch(UIDs[0], [b'ENVELOPE'])
        messages = server.fetch(UIDs, [b'BODY[]'])
        envelopes = server.fetch(UIDs, [b'ENVELOPE'])

        print(UIDs)
        mails = []
        for UID in messages.keys():
            mail = Mail()
            # Parse the raw email message.
            message = pyzmail.PyzMessage.factory(messages[UID][b'BODY[]'])
            if message.html_part is not None:
                body = message.html_part.get_payload()
                html = True
            if message.text_part is not None:
                # If there's both an html and text part, use the text part.
                body = message.text_part.get_payload()
                html = False

            # pdb.set_trace()
            # save desirables
            envelope = envelopes[UID][b'ENVELOPE']
            mail.to = _address_to_email(envelope.to)
            mail.fro = _address_to_email(envelope.from_)[0]
            mail.body = body.decode()
            mail.subject = envelope.subject.decode()
            mail.reply_to = _address_to_email(envelope.reply_to)
            mail.date = envelope.date
            mail.message_id = message.get("Message-ID")
            mail.raw_message = message
            mail.uid = UID
            mail.html = html

            mails.append(mail)

    return mails


def delete_answered_emails(UIDs, cfg):
    """
    1. Log in to the email server.
    2. Read ENVELOPE and BODY
    3. Put essentials together
    """

    with imapclient.IMAPClient(cfg.IMAP_SERVER, ssl=True) as server:
        server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
        server.select_folder('INBOX')
        logging.debug('Connected. %s' % server.welcome)

        # Delete the emails, if there are any.
        if UIDs:
            server.delete_messages(UIDs)
            server.expunge()
            # server.move(UIDs, imapclient.imapclient.SENT)
            # server.move(UIDs,
            #             server.find_special_folder(imapclient.imapclient.SENT))

        # server.logout()  # unnecessary


def _address_to_email(address):
    return list([x.decode() for x in
                 [b'%s@%s' % (x, y) for a, b, x, y in address]])
