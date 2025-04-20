import smtplib
from email.message import EmailMessage
from config import EMAIL_USER, NOTIFY_TO, EMAIL_PASS


def send_notification(subject: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = NOTIFY_TO
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
