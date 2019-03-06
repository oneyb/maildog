#!/usr/bin/env python3

import smtpd
import asyncore


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        import pdb; pdb.set_trace()
        print('Receiving message from:', peer)
        print('Message addressed from:', mailfrom)
        print('Message addressed to :', rcpttos)
        print('Message length:', len(data))


server = CustomSMTPServer(('127.0.0.1', 1025), None)
asyncore.loop()
