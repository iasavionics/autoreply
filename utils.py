import email
from email.utils import parseaddr
from bs4 import BeautifulSoup


AUTO_SUBJECTS = [
    "auto reply",
    "out of office",
    "automatic reply",
    "vacation"
]


def is_mailer_daemon(msg):

    sender = str(msg.get("From", "")).lower()

    if "mailer-daemon" in sender:
        return True

    if "postmaster" in sender:
        return True

    return False


def is_auto_email(msg):

    subject = str(msg.get("Subject", "")).lower()

    for word in AUTO_SUBJECTS:

        if word in subject:
            return True

    if msg.get("Auto-Submitted"):
        return True

    return False


def get_reply_to(msg):

    reply_to = msg.get("Reply-To")

    if reply_to:
        return parseaddr(reply_to)[1]

    return parseaddr(
        msg.get("From")
    )[1]


def extract_cc(msg):

    cc_list = []

    if msg.get("Cc"):

        addresses = email.utils.getaddresses(
            [msg.get("Cc")]
        )

        for name, addr in addresses:
            cc_list.append(addr)

    return cc_list


def extract_body(msg):

    if msg.is_multipart():

        for part in msg.walk():

            if part.get_content_type() == "text/html":

                return part.get_payload(
                    decode=True
                ).decode(errors="ignore")

            if part.get_content_type() == "text/plain":

                return part.get_payload(
                    decode=True
                ).decode(errors="ignore")

    return msg.get_payload(
        decode=True
    ).decode(errors="ignore")


def build_outlook_quote(msg, body):

    sender = msg.get("From", "")
    date = msg.get("Date", "")
    to = msg.get("To", "")
    subject = msg.get("Subject", "")

    header = f"""
<hr>
<b>From:</b> {sender}<br>
<b>Sent:</b> {date}<br>
<b>To:</b> {to}<br>
<b>Subject:</b> {subject}<br><br>
"""

    soup = BeautifulSoup(
        body,
        "html.parser"
    )

    return header + str(soup)