import smtplib
from email.message import EmailMessage


def send_mail(
        subject: str,
        message_plain: str,
        sender: str,
        to: str,
        message_html=None,
):
    """Send mail to the specified email address
    sender:  ("email", "fullname", "shortname")
    to: "email"
    """
    msg = EmailMessage()

    msg['Subject'] = subject
    msg['From'] = [sender]
    msg['To'] = to
    msg.set_content(message_plain)

    if message_html:
        msg.add_alternative(message_html, subtype='html')
    try:
        with smtplib.SMTP('localhost', port=25) as s:
            s.send_message(msg)
    except Exception as e:
        print("Error connecting smtp and send error: {}".format(e))
