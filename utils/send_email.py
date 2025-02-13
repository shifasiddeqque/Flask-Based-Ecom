from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.config import MailConfig

email = Mail()  # Create a Mail instance

def init_app(app):
    """
    Initialize the Flask-Mail extension with the Flask app.
    """
    email.init_app(app)

def send_mail(subject, recipient, body):
    """
    Function to send an email using Gmail SMTP.
    """
    sender_email = MailConfig.sender_email  # Get the sender email from config

    if isinstance(recipient, list):
        recipient = recipient[0]

    recipient = str(recipient)

    subject = str(subject)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a connection with the Gmail SMTP server
        with smtplib.SMTP(MailConfig.smtp_server, MailConfig.smtp_port) as server:
            server.starttls()  # Secure the connection with TLS
            server.login(MailConfig.username, MailConfig.password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient, text)
    except Exception as e:
        print(f"Failed to send email: {e}")