import imaplib
import email
import threading
from reply_sender import send_reply
from config import *
import time

replied_ids = set()

def is_ignored_email(msg):
    subject = (msg.get("Subject") or "").lower()
    if any(x in subject for x in ["mailer-daemon", "failure notice", "undeliverable", "return to sender"]):
        return True
    auto_headers = [
        "auto-submitted",
        "x-auto-response-suppress",
        "x-webmin-autoreply",
        "x-ms-exchange-generated-message-source"
    ]
    for header in auto_headers:
        val = msg.get(header) or msg.get(header.lower()) or ""
        if val.lower() in ("auto-replied", "all", "auto-generated", "mailbox rules agent", "1"):
            return True
    return False

def create_folder_if_not_exists(imap, folder_name):
    status, folders = imap.list()
    folder_names = [f.decode().split(' "/" ')[-1] for f in folders]
    if folder_name not in folder_names:
        imap.create(folder_name)

def mark_as_read_and_move(imap, mail_id, folder_name):
    imap.store(mail_id, '+FLAGS', '\\Seen')
    imap.copy(mail_id, folder_name)
    imap.store(mail_id, '+FLAGS', '\\Deleted')
    imap.expunge()

def start_listener():
    imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    imap.select("INBOX")

    while True:
        status, messages = imap.search(None, "UNSEEN")
        mail_ids = messages[0].split()
        for mail_id in mail_ids:
            status, msg_data = imap.fetch(mail_id, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            if is_ignored_email(msg):
                create_folder_if_not_exists(imap, "Ignored")
                mark_as_read_and_move(imap, mail_id, "Ignored")
                continue

            msg_id = msg.get("Message-ID")
            if not msg_id or msg_id in replied_ids:
                continue

            replied_ids.add(msg_id)
            threading.Timer(REPLY_DELAY, send_reply, args=[msg]).start()

            create_folder_if_not_exists(imap, "Answered")
            mark_as_read_and_move(imap, mail_id, "Answered")

        time.sleep(10)