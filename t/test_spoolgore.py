#!/usr/bin/env python
# encoding: utf-8

import smtpd
import time
import asyncore
import threading
import nose
import unittest

import os.path

from email.mime.text import MIMEText
from nose.tools import assert_equals


SPOOL_DIRECTORY = "/tmp/spoolgore_t"
JSON_STATS = os.path.join(SPOOL_DIRECTORY, ".spoolgore.js")

LOCAL_ADDRESS = ("127.0.0.1", 8025)
REMOTE_ADDRESS = ("127.0.0.1", 8026)

DEFAULT_SENDER = "foo@bar.com"
DEFAULT_RECEIVER = "jhon@doe.com"
DEFAULT_SUBJECT = "Look, an email!"


class MockSMTPServer(smtpd.SMTPServer, object):

    def __init__(self, localhost, remotehost):
        super(MockSMTPServer, self).__init__(localhost, remotehost)
        self.mails = dict()

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.mails[mailfrom] = data

    def clear(self):
        self.mails = dict()

    @property
    def count(self):
        return len(self.mails)


def spoool_mail(content, sender, receiver, subject=None):
    """
    Put mail in the spooler directory.
    Sender and receiver must be mail Address.
    """
    msg = MIMEText(content)
    msg['From'] = sender
    msg['To'] = receiver

    if subject:
        msg['Subject'] = subject

    with open(os.path.join(SPOOL_DIRECTORY, str(time.time())), 'w') as mail_f:
        mail_f.write(msg.as_string())


class TestSpoolgore(unittest.TestSuite, object):

    def setup(self):
        "Setup test fixtures here."
        self.server = MockSMTPServer(LOCAL_ADDRESS, REMOTE_ADDRESS)

        self.thread = threading.Thread(
            target=asyncore.loop, name="Asyncore Loop", kwargs={'timeout': 1}
        )
        self.thread.daemon = True
        self.thread.start()

    def teardown(self):
        "Teardown test fixtures here"
        pass
        # self.server.close()
        # self.thread.join()

    def test_base_mail(self):
        spoool_mail(
            "Base email check", DEFAULT_SENDER, DEFAULT_RECEIVER, DEFAULT_SUBJECT
        )
        time.sleep(10)
        assert_equals(self.server.count, 1)


def main():
    nose.main()

if __name__ == '__main__':
    main()
