#!/usr/bin/env python
#@author : wklken@yeah.ent
#@version : 0.1
#@desc: for mail sending.

import smtplib
import getopt
import sys
import os

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase

from email.MIMEText import MIMEText
import email.Encoders as encoders


def send_mail(mail_from, mail_to, subject, msg_txt, files=[]):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = mail_to

    # Create the body of the message (a plain-text and an HTML version).
    #text = msg
    html = msg_txt

    # Record the MIME types of both parts - text/plain and text/html.
    #part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    #msg.attach(part1)
    msg.attach(part2)

    #attachment
    for f in files:
        #octet-stream:binary data
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.

    mailto_list = mail_to.strip().split(",")
    if len(mailto_list) > 1:
        for mailtoi in mailto_list:
            s.sendmail(mail_from, mailtoi.strip(), msg.as_string())
    else:
        s.sendmail(mail_from, mail_to, msg.as_string())

    s.quit()
    return True


def main():
    files = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:t:s:m:a:")
        for op, value in opts:
            if op == "-f":
                mail_from = value
            elif op == "-t":
                mail_to = value
            elif op == "-s":
                subject = value
            elif op == "-m":
                msg_txt = value
            elif op == "-a":
                files = value.split(",")
    except getopt.GetoptError:
        print(sys.argv[0] + " : params are not defined well!")

    print mail_from, mail_to, subject, msg_txt
    if files:
        send_mail(mail_from, mail_to, subject, msg_txt, files)
    else:
        send_mail(mail_from, mail_to, subject, msg_txt)

if __name__ == "__main__":
    main()
