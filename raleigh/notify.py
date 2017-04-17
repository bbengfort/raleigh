# notify
# Quickly send email from the command line with gmail.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Apr 17 11:34:55 2017 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: notify.py [] benjamin@bengfort.com $

"""
Quickly send email from the command line with gmail.
"""

##########################################################################
## Imports
##########################################################################

import os
import smtplib

from email import encoders
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from datetime import datetime, timezone


##########################################################################
## Message Environment
##########################################################################

EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")


##########################################################################
## Message Constants
##########################################################################

HUMAN_DATETIME  = "%A, %B %d %Y at %H:%M:%S %z"
DEFAULT_SUBJECT = "Server Notification"
DEFAULT_MESSAGE = "A notification was triggered on {}"


##########################################################################
## Email Notifications
##########################################################################

def notify(recipient, subject=None, message=None, **kwargs):
    """
    Notifies the recipient at the given email address by sending an email
    with the subject and message in it. Meant to be used sparingly.
    """

    # Get the default subject and message
    subject = subject or DEFAULT_SUBJECT
    message = message or DEFAULT_MESSAGE.format(
        datetime.now(timezone.utc).astimezone().strftime(HUMAN_DATETIME)
    )

    # Get the arguments from the settings
    sender   = kwargs.get('sender', EMAIL_USERNAME)
    username = kwargs.get('username', EMAIL_USERNAME)
    password = kwargs.get('password', EMAIL_PASSWORD)
    host     = kwargs.get('host', EMAIL_HOST)
    port     = kwargs.get('port', EMAIL_PORT)
    mimetype = kwargs.get('mimetype', 'plain')
    fail_silent = kwargs.get('fail_silent', False)

    # Create the email message
    msg = MIMEMultipart()
    msg['From']= sender
    msg['To'] = recipient
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    # Attach the mime text to the message
    msg.attach(MIMEText(message, mimetype))

    # Attach any files to the email
    for fpath in kwargs.get('files', []):
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(fpath, 'rb').read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition', 'attachment; filename={}'.format(
                os.path.basename(fpath)
            )
        )
        msg.attach(part)

    # Attempt to send the message
    try:

        # Do the smtp thing
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(username, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()

        # Return message success
        return True

    except Exception as e:
        if not fail_silent:
            raise e

        # Return message failure
        return False
