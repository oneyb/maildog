#!/usr/bin/env python3

# import pdb
import imapclient
# import pyzmail
import email.parser
import logging
from . import Mail


def get_new_emails(cfg):
    """
    1. Log in to the email server.
    2. Fetch ENVELOPE and BODY
    3. Put essentials together
    """

    def _address_to_email(address):
        return list([x.decode() for x in
                     [b'%s@%s' % (x, y) for a, b, x, y in address]])

    print("Connecting")
    with imapclient.IMAPClient(cfg.IMAP_SERVER, ssl=cfg.MAILDOG_SSL) as server:
        server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
        server.select_folder('INBOX')
        logging.debug('Connected. %s' % server.welcome)

        # Fetch all instruction emails.
        UIDs = server.search("UNANSWERED")
        # print(UIDs)
        messages = server.fetch(UIDs, [b'RFC822'])
        # envelopes = server.fetch(UIDs, [b'ENVELOPE'])

        mails = []
        for UID in messages.keys():
            mail = Mail()
            # Parse the raw email message.
            ep = email.parser.BytesFeedParser()
            ep.feed(messages[UID][b'RFC822'])
            message = ep.close()
            # import pdb; pdb.set_trace()
            # message = pyzmail.PyzMessage.factory(messages[UID][b'BODY[]'])
            if message.get_content_type() == 'text/html':
                mail.html = True
            else:
                mail.html = False

            # pdb.set_trace()
            # save desirables
            mail.to = message['To']
            mail.fro = message['From']
            mail.body = message.get_payload()
            mail.subject = message['Subject']
            mail.reply_to = [message.get('Reply-To', mail.fro)]
            if not mail.reply_to:
                mail.reply_to = [(mail.fro)]
            mail.date = message['Date']
            mail.message_id = message.get("Message-ID")
            mail.raw_message = message
            mail.uid = UID

            mails.append(mail)

    return mails


def delete_answered_emails(UIDs, cfg):
    """
    1. Log in to the email server.
    2. Mark ANSWERED emails as deleted.
    3. Expunge (have server actually delete them).
    """

    with imapclient.IMAPClient(cfg.IMAP_SERVER, ssl=True) as server:
        server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
        server.select_folder('INBOX')
        UIDs = server.search("ANSWERED")
        logging.debug('Connected. %s' % server.welcome)

        # Delete the emails, if there are any.
        if UIDs:
            server.delete_messages(UIDs)
            server.expunge()
            # server.move(UIDs, imapclient.imapclient.SENT)
            # server.move(UIDs,
            #             server.find_special_folder(imapclient.imapclient.SENT))

        # server.logout()  # unnecessary


def copy_sent_messages_and_delete_answered_emails(mails, cfg):
    """
    1. Log in to the email server.
    2. Mark ANSWERED emails as deleted.
    3. Expunge (have server actually delete them).
    """

    with imapclient.IMAPClient(cfg.IMAP_SERVER, ssl=True) as server:
        server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
        server.select_folder('INBOX')
        UIDs = server.search("ANSWERED")
        logging.debug('Connected. %s' % server.welcome)

        for msg in mails:
            result = server.append('Sent', r'(READ)', msg.reply_message.as_string())
            # server.move(UIDs, imapclient.imapclient.SENT)
            # server.move(UIDs,
            #             server.find_special_folder(imapclient.imapclient.SENT))
        # # Delete the emails, if there are any.
        # if UIDs:
        #     server.delete_messages(UIDs)
        #     server.expunge()



