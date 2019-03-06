#!/usr/bin/env python3

# import pdb
import imapclient
# import pyzmail
import email.parser
import logging
from . import Mail


def get_new_emails(cfg, message_flags=['re:', 'aw:', 'fw:', 'wg:']):
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
        server.select_folder('Sent')
        sent_UIDs = server.search()
        envelopes = server.fetch(sent_UIDs[:23], [b'ENVELOPE'])
        message_ids_processed = [ x[b'ENVELOPE'].in_reply_to  for y, x in envelopes.items()]

        mails = []
        for UID in messages.keys():
            mail = Mail()
            # Parse the raw email message.
            # ep = email.parser.FeedParser()
            # ep.feed(messages[UID][b'RFC822'].decode())
            ep = email.parser.BytesFeedParser()
            ep.feed(messages[UID][b'RFC822'])
            message = ep.close()
            encoding = message.get_charset()
            if not encoding:
                encoding = message.get_charsets()[0]
            if message.get_default_type() == 'text/html':
                mail.html = True
            else:
                mail.html = False

            # save desirables
            mail.subject = message['Subject']
            if [x for x in message_flags if x in mail.subject.lower()]:
                del mail
                continue

            mail.to = message['To']
            mail.fro = message['From']
            body = message.get_payload(decode=True)
            if isinstance(body, list):
                mail.body = body[0].decode()
            elif not body:
                mail.body = message.get_payload(0).get_payload()
            else:
                mail.body = body.decode()

            mail.reply_to = [message.get('Reply-To', mail.fro)]
            if not mail.reply_to:
                mail.reply_to = [(mail.fro)]
            mail.date = message['Date']
            mail.message_id = message.get("Message-ID")
            if mail.message_id in message_ids_processed:
                del mail
                continue
            mail.raw_message = message
            mail.uid = UID

            mails.append(mail)

    return mails


def delete_answered_emails(UIDs, cfg):
    """
    1. Log in to the email server.
    2. *Flag* ANSWERED emails as \\deleted.
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


def copy_to_sent_and_delete(mails, cfg):
    """
    1. Log in to the email server.
    2. APPEND sent message to Sent folder
    3. If successful, *flag* original message as \\Deleted
    4. Expunge (have server actually delete them).
    """

    with imapclient.IMAPClient(cfg.IMAP_SERVER, ssl=True) as server:
        server.login(cfg.MAILDOG_EMAIL, cfg.MAILDOG_EMAIL_PASSWORD)
        server.select_folder('INBOX')
        # UIDs = server.search("ANSWERED")
        logging.debug('Connected. %s' % server.welcome)

        results = {}
        for msg in mails:
            res_append = server.append('Sent', msg.reply_message.as_string(),
                                       [r'\Seen'])
            if b'APPEND completed' in res_append:
                res_mark = server.add_flags(msg.uid, [r'\Seen', r'\Deleted'])
            # server.move(UIDs, imapclient.imapclient.SENT)
            # server.move(UIDs,
            #             server.find_special_folder(imapclient.imapclient.SENT))
            results[msg.uid] = res_append
        # Delete the emails, if there are any.
        # import pdb; pdb.set_trace()
        # server.delete_messages(UIDs)
        server.expunge()
    return results
