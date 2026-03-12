import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr

from config import *
from utils import extract_body, build_outlook_quote, get_reply_to, extract_cc

# keep a set of replied Message-IDs to prevent duplicates
replied_ids = set()

MAILFROM = "brett.c.gerry@boeing.cam"

def attach_cid_images(message):
    folder = "cid_images"
    if not os.path.isdir(folder):
        return
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            cid = os.path.splitext(file)[0]
            img.add_header("Content-ID", f"<{cid}>")
            img.add_header("Content-Disposition", "inline", filename=file)
            message.attach(img)

def send_reply(original_msg):
    global replied_ids

    msg_id = original_msg.get("Message-ID")
    if not msg_id or msg_id in replied_ids:
        return  # already replied or no ID

    replied_ids.add(msg_id)

    reply_to = get_reply_to(original_msg)
    cc = extract_cc(original_msg)
    recipients = [reply_to] + cc

    subject = original_msg.get("Subject", "")
    body = extract_body(original_msg)
    quote = build_outlook_quote(original_msg, body)

    # Load template
    with open("template.html") as f:
        template = f.read()

    quote_html = f'<div style="margin-top:20px;padding-left:10px;border-left:2px solid #ccc">{quote}</div>'

    html = f"<html><body>{template}{quote_html}</body></html>"

    msg = MIMEMultipart("related")
    msg["Subject"] = "RE: " + subject
    msg["From"] = formataddr((FROM_NAME, MAILFROM))
    msg["To"] = reply_to
    if cc:
        msg["Cc"] = ",".join(cc)

    # **Threading headers**
    msg["In-Reply-To"] = msg_id
    msg["References"] = msg_id

    msg.attach(MIMEText(html, "html"))
    attach_cid_images(msg)

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.starttls()
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.sendmail(MAILFROM, recipients, msg.as_string())
    smtp.quit()

    print("Reply sent to:", reply_to)