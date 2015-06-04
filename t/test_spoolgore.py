#!/usr/bin/env python
# encoding: utf-8

import time
import asyncore
import threading
import unittest
import os
import signal
import json
import subprocess
import shutil
import secure_smtpd
# import smtpd

import os.path

from email.mime.text import MIMEText
from nose.tools import assert_equals, assert_is_not_none, assert_false, nottest

SPOOLGORE_EXECUTABLE = "./spoolgore"

SPOOL_DIRECTORY = "/tmp/spoolgore_t"
JSON_STATS = os.path.join(SPOOL_DIRECTORY, ".spoolgore.js")

LOCAL_ADDRESS = ("127.0.0.1", 8025)
LOCAL_ADDRESS_S = ':'.join([str(s) for s in LOCAL_ADDRESS])

DEFAULT_SENDER = "foo@bar.com"
DEFAULT_RECEIVER = "jhon@doe.com"
DEFAULT_SUBJECT = "Look, an email!"

EVENT_TIMEOUT = 10


def setup_module():
    try:
        os.mkdir(SPOOL_DIRECTORY)
    except OSError:
        pass


def teardown_module():
    shutil.rmtree(SPOOL_DIRECTORY, ignore_errors=True)


class MockSMTPServer(secure_smtpd.SMTPServer, object):

    def __init__(self, localhost, fake_errors=False):
        super(MockSMTPServer, self).__init__(
            localhost,
            None,
            process_count=1
        )
        self.fake_errors = fake_errors
        self.mails = list()
        self.event = threading.Event()

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.mails.append(data)
        self.event.set()

        if self.fake_errors:
            return '500 Generic Error'
        return None

    def clear(self):
        self.mails = list()
        self.event.clear()

    @property
    def count(self):
        return len(self.mails)

    @property
    def last(self):
        if self.mails:
            return self.mails[-1]
        return None


def spoool_mail(content, sender=DEFAULT_SENDER, receiver=DEFAULT_RECEIVER, subject=DEFAULT_SUBJECT):
    """
    Put mail in the spooler directory.
    """
    msg = MIMEText(content)
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    path = os.path.join(SPOOL_DIRECTORY, str(time.time()))

    with open(path, "w") as mail_f:
        mail_f.write(msg.as_string())

    return path


def start_spoolgore(arguments):
    arguments = [SPOOLGORE_EXECUTABLE] + arguments
    return subprocess.Popen(arguments, shell=False)


class TestSpoolgore(unittest.TestSuite, object):

    @classmethod
    def setup_class(cls):
        cls.spoolgore = start_spoolgore(["-smtpaddr", LOCAL_ADDRESS_S, "-attempts", "5", "-freq", "1", SPOOL_DIRECTORY])

        cls.server = MockSMTPServer(LOCAL_ADDRESS)

        cls.thread = threading.Thread(
            target=asyncore.loop, kwargs={'timeout': 1}
        )
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def teardown_class(cls):
        cls.spoolgore.terminate()

        cls.server.close()
        cls.thread.join()

    def teardown(self):
        self.server.clear()

    def test_base_mail(self):
        spoool_mail("Base email check")

        self.spoolgore.send_signal(signal.SIGURG)
        self.server.event.wait()

        assert_equals(self.server.count, 1)
        mail = self.server.last
        assert_is_not_none(mail)

    @nottest
    def test_attempts(self):
        self.server.fake_errors = True

        path = spoool_mail("Base email with attempts")
        for i in range(5):
            self.spoolgore.send_signal(signal.SIGURG)
            self.server.event.wait()
            self.server.event.clear()

        time.sleep(1)
        with open(JSON_STATS) as json_stats:
            j = json.loads(json_stats.read())
            assert_false(path in j)

        self.server.fake_errors = False
