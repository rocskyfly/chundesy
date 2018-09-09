# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import atexit

sys.path.append("..")
from plugins import Email
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from . import app_utils
import time
import sys

if sys.version_info < (3, 0):
    import Queue as queue  # Python 2
else:
    import queue  # Python 3


class Notifier(object):
    class NotificationClient(object):
        def __init__(self, gather, timestamp):
            self.gather = gather
            self.timestamp = timestamp

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, profile, brain):
        self._logger = logging.getLogger(__name__)
        self.q = queue.Queue()
        self.profile = profile
        self.notifiers = []
        self.brain = brain

        if 'email' in profile and ('enable' not in profile['email'] or profile['email']['enable']):
            self.notifiers.append(self.NotificationClient(self.handleEmailNotifications, None))
        else:
            self._logger.debug('email account not set in profile, email notifier will not be used')

        if 'robot' in profile and profile['robot'] == 'emotibot':
            self.notifiers.append(self.NotificationClient(self.handleRemenderNotifications, None))

        sched = BackgroundScheduler(daemon=True)
        sched.add_job(self.gather, 'interval', seconds=120)
        sched.start()
        atexit.register(lambda: sched.shutdown(wait=False))

    def gather(self):
        [client.run() for client in self.notifiers]

    def handleEmailNotifications(self, lastDate):
        """Places new email notifications in the Notifier's queue."""
        emails = Email.fetchUnreadEmails(self.profile, since=lastDate)
        if emails is None:
            return
        if emails:
            lastDate = Email.getMostRecentDate(emails)

        def styleEmail(mail):
            subject = Email.getSubject(mail, self.profile)
            if Email.isEchoEmail(mail, self.profile):
                if Email.isNewEmail(mail):
                    return subject.replace('[echo]', '')
                else:
                    return ""
            elif Email.isControlEmail(mail, self.profile):
                self.brain.query([subject.replace('[control]', '').strip()], None, True)
                return ""
            sender = Email.getSender(mail)

            return "您有来自 %s 的新邮件 %s" % (sender, subject)

        for mail in emails:
            self.q.put(styleEmail(mail))

        return lastDate

    def handleRemenderNotifications(self, lastDate):
        lastDate = time.strftime('%d %b %Y %H:%M:%S')
        due_reminders = app_utils.get_due_reminders()
        for reminder in due_reminders:
            self.q.put(reminder)

        return lastDate

    def getNotification(self):
        """Returns a notification. Note that this function is consuming."""
        try:
            notif = self.q.get(block=False)
            return notif
        except queue.Empty:
            return None

    def getAllNotifications(self):
        """
            Return a list of notifications in chronological order.
            Note that this function is consuming, so consecutive calls
            will yield different results.
        """
        notifs = []

        notif = self.getNotification()
        while notif:
            notifs.append(notif)
            notif = self.getNotification()

        return notifs
